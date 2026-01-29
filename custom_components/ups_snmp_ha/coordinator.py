# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2026 Anthony Burow
# https://github.com/aburow/ups-snmp-ha

"""SNMP data coordinator for UPS sensors."""

from __future__ import annotations

import asyncio
import logging
import re
import time
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .snmp_helper import async_get_snmp_values

_LOGGER = logging.getLogger(__name__)

UPS_MIB = "ups_mib"
APC_MIB = "apc_mib"


UPS_MIB_OIDS: dict[str, dict[str, Any]] = {
    "manufacturer": {"oid": "1.3.6.1.2.1.33.1.1.1.0"},
    "model": {"oid": "1.3.6.1.2.1.33.1.1.2.0"},
    "firmware": {"oid": "1.3.6.1.2.1.33.1.1.3.0"},
    "name": {"oid": "1.3.6.1.2.1.33.1.1.5.0"},
    "battery_status": {"oid": "1.3.6.1.2.1.33.1.2.1.0"},
    "seconds_on_battery": {"oid": "1.3.6.1.2.1.33.1.2.2.0"},
    "runtime_remaining": {"oid": "1.3.6.1.2.1.33.1.2.3.0"},
    "battery_charge": {"oid": "1.3.6.1.2.1.33.1.2.4.0"},
    "battery_voltage": {"oid": "1.3.6.1.2.1.33.1.2.5.0", "scale": 0.1},
    "battery_temperature": {"oid": "1.3.6.1.2.1.33.1.2.7.0"},
    "input_line_count": {"oid": "1.3.6.1.2.1.33.1.3.2.0"},
    "input_frequency": {"oid": "1.3.6.1.2.1.33.1.3.3.1.2.1", "scale": 0.1},
    "input_voltage": {"oid": "1.3.6.1.2.1.33.1.3.3.1.3.1"},
    "input_current": {"oid": "1.3.6.1.2.1.33.1.3.3.1.4.1", "scale": 0.1},
    "input_power": {"oid": "1.3.6.1.2.1.33.1.3.3.1.5.1"},
    "output_source_raw": {"oid": "1.3.6.1.2.1.33.1.4.1.0"},
    "output_frequency": {"oid": "1.3.6.1.2.1.33.1.4.2.0", "scale": 0.1},
    "output_line_count": {"oid": "1.3.6.1.2.1.33.1.4.3.0"},
    "bypass_frequency": {"oid": "1.3.6.1.2.1.33.1.5.1.0", "scale": 0.1},
    "bypass_line_count": {"oid": "1.3.6.1.2.1.33.1.5.2.0"},
    "alarms_present": {"oid": "1.3.6.1.2.1.33.1.6.1.0"},
}

APC_MIB_OIDS: dict[str, dict[str, Any]] = {
    "model": {"oid": "1.3.6.1.4.1.318.1.1.1.1.1.1.0"},
    "name": {"oid": "1.3.6.1.4.1.318.1.1.1.1.1.2.0"},
    "firmware": {"oid": "1.3.6.1.4.1.318.1.1.1.1.2.1.0"},
    "serial_number": {"oid": "1.3.6.1.4.1.318.1.1.1.1.2.3.0"},
    "battery_status": {"oid": "1.3.6.1.4.1.318.1.1.1.2.1.1.0"},
    "battery_charge": {"oid": "1.3.6.1.4.1.318.1.1.1.2.2.1.0"},
    "battery_temperature": {"oid": "1.3.6.1.4.1.318.1.1.1.2.2.2.0"},
    "runtime_remaining": {"oid": "1.3.6.1.4.1.318.1.1.1.2.2.3.0", "timeticks_minutes": True},
    "output_source_raw": {"oid": "1.3.6.1.4.1.318.1.1.1.4.1.1.0"},
    "output_voltage": {"oid": "1.3.6.1.4.1.318.1.1.1.4.2.1.0"},
    "output_frequency": {"oid": "1.3.6.1.4.1.318.1.1.1.4.2.2.0"},
    "output_load": {"oid": "1.3.6.1.4.1.318.1.1.1.4.2.3.0"},
    "input_voltage": {"oid": "1.3.6.1.4.1.318.1.1.1.3.2.1.0"},
    "input_frequency": {"oid": "1.3.6.1.4.1.318.1.1.1.3.2.4.0"},
}

UPS_OUTPUT_SOURCE_MAP = {
    1: "other",
    2: "none",
    3: "normal",
    4: "bypass",
    5: "battery",
    6: "booster",
    7: "reducer",
}

APC_OUTPUT_SOURCE_MAP = {
    1: "other",
    2: "normal",
    3: "battery",
    4: "bypass",
}

BATTERY_STATUS_MAP = {
    1: "unknown",
    2: "normal",
    3: "low",
    4: "depleted",
}


class UpsSnmpCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that polls UPS data via SNMP."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        community: str,
        device_name: str,
        fast_poll_interval: int,
        slow_poll_interval: int,
        entry_id: str,
    ) -> None:
        fast_interval = max(1, int(fast_poll_interval))
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=fast_interval),
        )
        self.host = host
        self.community = community
        self.device_name = device_name
        self.fast_poll_interval = fast_interval
        self.slow_poll_interval = max(10, int(slow_poll_interval))
        self._last_slow_poll = 0.0
        self.protocol: str | None = None
        self.snmp_version = "2c"

        self.data: dict[str, Any] = {}
        self.manufacturer: str | None = None
        self.hw_model: str | None = None
        self.serial_number: str | None = None
        self.fw_version: str | None = None
        self._entry_id = entry_id

        locks = hass.data[DOMAIN].setdefault("snmp_locks", {})
        self._io_lock = locks.setdefault(self.host, asyncio.Lock())

        self._failure_count = 0
        self._backoff_until = 0.0
        self._backoff_base = 2
        self._backoff_max = 60

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from UPS via SNMP."""
        now = time.monotonic()

        if self._backoff_until and now < self._backoff_until:
            raise UpdateFailed(
                f"{self.device_name} {self.host}: backoff active for {self._backoff_until - now:.1f}s"
            )

        _LOGGER.debug(
            "Starting SNMP update for %s (%s, entry_id=%s)",
            self.device_name,
            self.host,
            self._entry_id,
        )

        lock_started = time.monotonic()
        try:
            async with self._io_lock:
                waited = time.monotonic() - lock_started
                if waited > 0.001:
                    _LOGGER.debug(
                        "Waited %.3fs for SNMP lock (%s, entry_id=%s)",
                        waited,
                        self.host,
                        self._entry_id,
                    )
                data = await self._async_update_data_locked(now)
        except Exception as err:
            self._handle_update_failure(err)
            if isinstance(err, UpdateFailed):
                raise
            raise UpdateFailed(str(err)) from err

        self._failure_count = 0
        self._backoff_until = 0.0
        return data

    async def _async_update_data_locked(self, now: float) -> dict[str, Any]:
        """Fetch data from UPS via SNMP with the I/O lock held."""
        if self.protocol is None:
            await self._detect_protocol()

        protocol_oids = UPS_MIB_OIDS if self.protocol == UPS_MIB else APC_MIB_OIDS
        fast_keys = {
            "output_source_raw",
            "runtime_remaining",
            "seconds_on_battery",
            "battery_charge",
            "input_voltage",
        }
        fast_data = await self._fetch_keys(protocol_oids, fast_keys)

        slow_data: dict[str, Any] = {}
        if now - self._last_slow_poll >= self.slow_poll_interval or self._last_slow_poll == 0.0:
            slow_keys = set(protocol_oids.keys()) - fast_keys
            slow_data = await self._fetch_keys(protocol_oids, slow_keys)
            if slow_data:
                self._last_slow_poll = now

        if not fast_data and not slow_data and not self.data:
            raise UpdateFailed("No SNMP data returned")

        data: dict[str, Any] = {**self.data, **slow_data, **fast_data}

        data.update(self._derive_states(data))
        self._update_metadata(data)

        return data

    def _handle_update_failure(self, err: Exception) -> None:
        """Apply backoff for repeated failures."""
        self._failure_count += 1
        backoff = min(self._backoff_max, self._backoff_base**self._failure_count)
        self._backoff_until = time.monotonic() + backoff
        _LOGGER.warning(
            "SNMP update failed for %s (%s, entry_id=%s): %s; backing off for %.1fs",
            self.device_name,
            self.host,
            self._entry_id,
            err,
            backoff,
        )

    async def _detect_protocol(self) -> None:
        """Detect which SNMP MIB is available and the SNMP version."""
        for version in ("2c", "1"):
            if await self._try_protocol(UPS_MIB, UPS_MIB_OIDS, version):
                self.protocol = UPS_MIB
                self.snmp_version = version
                return
            if await self._try_protocol(APC_MIB, APC_MIB_OIDS, version):
                self.protocol = APC_MIB
                self.snmp_version = version
                return

        self.protocol = UPS_MIB
        _LOGGER.warning("Unable to detect SNMP protocol for %s, defaulting to UPS-MIB", self.host)

    async def _try_protocol(self, protocol: str, oid_map: dict[str, dict[str, Any]], version: str) -> bool:
        """Try to fetch a single identifying OID."""
        if protocol == UPS_MIB:
            test_oid = oid_map["output_source_raw"]["oid"]
        else:
            test_oid = oid_map["model"]["oid"]

        values = await async_get_snmp_values(
            host=self.host,
            oids=[test_oid],
            community=self.community,
            timeout=5,
            version=version,
            hass=self.hass,
        )
        return values.get(test_oid) is not None

    async def _fetch_keys(self, oid_map: dict[str, dict[str, Any]], keys: set[str]) -> dict[str, Any]:
        """Fetch and normalize SNMP values for a set of keys."""
        oids = [oid_map[key]["oid"] for key in keys if key in oid_map]
        if not oids:
            return {}

        raw = await async_get_snmp_values(
            host=self.host,
            oids=oids,
            community=self.community,
            timeout=5,
            version=self.snmp_version,
            hass=self.hass,
        )

        data: dict[str, Any] = {}
        for key in keys:
            spec = oid_map.get(key)
            if not spec:
                continue
            oid = spec["oid"]
            value = self._coerce_snmp_value(raw.get(oid))
            if value is None:
                continue
            if spec.get("timeticks_minutes"):
                value = round(value / 6000, 1)
            scale = spec.get("scale")
            if scale is not None and isinstance(value, (int, float)):
                value = round(value * scale, 2)
            data[key] = value

        return data

    def _derive_states(self, data: dict[str, Any]) -> dict[str, Any]:
        """Derive human-readable and binary states."""
        output_source_raw = data.get("output_source_raw")
        derived: dict[str, Any] = {}

        battery_status = data.get("battery_status")
        if battery_status is not None:
            try:
                derived["battery_status_text"] = BATTERY_STATUS_MAP.get(
                    int(battery_status), "unknown"
                )
            except (TypeError, ValueError):
                derived["battery_status_text"] = "unknown"

        if output_source_raw is None:
            return derived

        if self.protocol == APC_MIB:
            source_map = APC_OUTPUT_SOURCE_MAP
            normal_values = {2, 4}
            battery_values = {3}
        else:
            source_map = UPS_OUTPUT_SOURCE_MAP
            normal_values = {3, 4}
            battery_values = {5}

        output_source_text = source_map.get(int(output_source_raw), "unknown")
        on_battery = int(output_source_raw) in battery_values
        ac_power = int(output_source_raw) in normal_values

        derived.update({
            "output_source": output_source_text,
            "on_battery": on_battery,
            "ac_power": ac_power,
            "on_bypass": output_source_text == "bypass",
        })

        return derived

    def _update_metadata(self, data: dict[str, Any]) -> None:
        """Update device metadata from SNMP data."""
        manufacturer = data.get("manufacturer")
        if not manufacturer and self.protocol == APC_MIB:
            manufacturer = "APC"

        self.manufacturer = manufacturer or self.manufacturer
        self.hw_model = data.get("model") or self.hw_model
        self.serial_number = data.get("serial_number") or self.serial_number
        self.fw_version = data.get("firmware") or self.fw_version

    @staticmethod
    def _coerce_snmp_value(value: Any) -> Any:
        """Normalize SNMP values into Python types."""
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return value
        text = str(value).strip()
        if not text:
            return None
        match = re.search(r"\((\d+)\)", text)
        if match:
            return int(match.group(1))
        if re.fullmatch(r"-?\d+", text):
            return int(text)
        if re.fullmatch(r"-?\d+\.\d+", text):
            return float(text)
        return text
