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
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .capability_profile_unified import (
    APC_MIB,
    APC_MIB_OIDS,
    REQUIRED_DEPENDENCY_KEYS,
    REQUIRED_PROFILE_KEYS,
    UPS_MIB,
    UPS_MIB_OIDS,
    fast_poll_keys_for,
)
from .const import (
    DOMAIN,
    SNMP_BINARY_SENSOR_DESCRIPTIONS,
    SNMP_SENSOR_DESCRIPTIONS,
)
from .sensor_availability_unified import (
    is_core_local_metric,
    resolve_canonical_metric,
)
from .snmp_helper import async_get_snmp_values

_LOGGER = logging.getLogger(__name__)

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
        self._unsupported_oids: set[str] = set()
        self._fast_poll_keys = fast_poll_keys_for(UPS_MIB)
        self._sensor_entity_keys = {d.key for d in SNMP_SENSOR_DESCRIPTIONS}
        self._binary_entity_keys = {d.key for d in SNMP_BINARY_SENSOR_DESCRIPTIONS}

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from UPS via SNMP."""
        now = time.monotonic()
        poll_start = time.monotonic()
        lock_wait = 0.0
        snmp_locked_elapsed = 0.0
        protocol_detect_elapsed = 0.0
        fast_fetch_elapsed = 0.0
        slow_fetch_elapsed = 0.0
        derive_elapsed = 0.0
        metadata_elapsed = 0.0

        if self._backoff_until and now < self._backoff_until:
            raise UpdateFailed(
                f"{self.device_name} {self.host}: backoff active for {self._backoff_until - now:.1f}s"
            )

        _LOGGER.info(
            "Starting update cycle for %s (%s, entry_id=%s)",
            self.device_name,
            self.host,
            self._entry_id,
        )

        lock_started = time.monotonic()
        try:
            async with self._io_lock:
                lock_wait = time.monotonic() - lock_started
                if lock_wait > 0.001:
                    _LOGGER.debug(
                        "Waited %.3fs for SNMP lock (%s, entry_id=%s)",
                        lock_wait,
                        self.host,
                        self._entry_id,
                    )
                locked_start = time.monotonic()
                data, phase_timings = await self._async_update_data_locked(now)
                snmp_locked_elapsed = time.monotonic() - locked_start
                protocol_detect_elapsed = phase_timings["protocol_detect"]
                fast_fetch_elapsed = phase_timings["fast_fetch"]
                slow_fetch_elapsed = phase_timings["slow_fetch"]
                derive_elapsed = phase_timings["derive"]
                metadata_elapsed = phase_timings["metadata"]
        except Exception as err:
            self._handle_update_failure(err)
            if isinstance(err, UpdateFailed):
                raise
            raise UpdateFailed(str(err)) from err

        self._failure_count = 0
        self._backoff_until = 0.0

        _LOGGER.info(
            "Update cycle complete in %.3fs for %s (%s, entry_id=%s)",
            snmp_locked_elapsed,
            self.device_name,
            self.host,
            self._entry_id,
        )
        _LOGGER.info(
            "Poll timing breakdown for %s (%s, entry_id=%s): total=%.3fs, lock_wait=%.3fs, "
            "snmp_locked=%.3fs, protocol_detect=%.3fs, fast_fetch=%.3fs, slow_fetch=%.3fs, "
            "derive=%.3fs, metadata=%.3fs",
            self.device_name,
            self.host,
            self._entry_id,
            time.monotonic() - poll_start,
            lock_wait,
            snmp_locked_elapsed,
            protocol_detect_elapsed,
            fast_fetch_elapsed,
            slow_fetch_elapsed,
            derive_elapsed,
            metadata_elapsed,
        )

        return data

    async def _async_update_data_locked(
        self, now: float
    ) -> tuple[dict[str, Any], dict[str, float]]:
        """Fetch data from UPS via SNMP with the I/O lock held."""
        protocol_detect_elapsed = 0.0
        fast_fetch_elapsed = 0.0
        slow_fetch_elapsed = 0.0
        derive_elapsed = 0.0
        metadata_elapsed = 0.0

        if self.protocol is None:
            protocol_detect_start = time.monotonic()
            await self._detect_protocol()
            protocol_detect_elapsed = time.monotonic() - protocol_detect_start

        protocol_oids = UPS_MIB_OIDS if self.protocol == UPS_MIB else APC_MIB_OIDS
        self._fast_poll_keys = fast_poll_keys_for(self.protocol)
        selected_keys = self._selected_poll_keys(protocol_oids)
        fast_keys = selected_keys & self._fast_poll_keys

        fast_fetch_start = time.monotonic()
        fast_data = await self._fetch_keys(protocol_oids, fast_keys)
        fast_fetch_elapsed = time.monotonic() - fast_fetch_start

        slow_data: dict[str, Any] = {}
        if (
            now - self._last_slow_poll >= self.slow_poll_interval
            or self._last_slow_poll == 0.0
        ):
            slow_keys = selected_keys - fast_keys
            slow_fetch_start = time.monotonic()
            slow_data = await self._fetch_keys(protocol_oids, slow_keys)
            slow_fetch_elapsed = time.monotonic() - slow_fetch_start
            if slow_data:
                self._last_slow_poll = now

        if not fast_data and not slow_data and not self.data:
            raise UpdateFailed("No SNMP data returned")

        data: dict[str, Any] = {**self.data, **slow_data, **fast_data}

        derive_start = time.monotonic()
        data.update(self._derive_states(data))
        derive_elapsed = time.monotonic() - derive_start

        metadata_start = time.monotonic()
        self._update_metadata(data)
        metadata_elapsed = time.monotonic() - metadata_start

        return data, {
            "protocol_detect": protocol_detect_elapsed,
            "fast_fetch": fast_fetch_elapsed,
            "slow_fetch": slow_fetch_elapsed,
            "derive": derive_elapsed,
            "metadata": metadata_elapsed,
        }

    def _selected_poll_keys(self, oid_map: dict[str, dict[str, Any]]) -> set[str]:
        """Return protocol OID keys to poll based on core and enabled entities."""
        protocol_keys = set(oid_map.keys())
        core_poll_keys = {key for key in protocol_keys if is_core_local_metric(key)}
        profile_keys = protocol_keys & REQUIRED_PROFILE_KEYS
        dependency_keys = protocol_keys & REQUIRED_DEPENDENCY_KEYS

        enabled_entity_keys = self._enabled_entity_keys()
        enabled_canonical_metrics = {
            canonical
            for key in enabled_entity_keys
            if (canonical := resolve_canonical_metric(key))
        }

        enabled_poll_keys = {
            key
            for key in protocol_keys
            if resolve_canonical_metric(key) in enabled_canonical_metrics
        }

        return core_poll_keys | profile_keys | dependency_keys | enabled_poll_keys

    def _enabled_entity_keys(self) -> set[str]:
        """Return local entity keys that are currently enabled in entity registry."""
        entity_registry = er.async_get(self.hass)
        enabled: set[str] = set()

        for key in self._sensor_entity_keys:
            unique_id = f"{DOMAIN}_{self._entry_id}_{key}"
            if self._is_entity_enabled(entity_registry, "sensor", unique_id, key):
                enabled.add(key)

        for key in self._binary_entity_keys:
            unique_id = f"{DOMAIN}_{self._entry_id}_{key}"
            if self._is_entity_enabled(
                entity_registry, "binary_sensor", unique_id, key
            ):
                enabled.add(key)

        return enabled

    @staticmethod
    def _is_entity_enabled(
        entity_registry: er.EntityRegistry,
        entity_domain: str,
        unique_id: str,
        local_key: str,
    ) -> bool:
        """Return whether an entity is enabled, honoring default core behavior."""
        entity_id = entity_registry.async_get_entity_id(
            entity_domain, DOMAIN, unique_id
        )
        default_enabled = is_core_local_metric(local_key)

        if entity_id is None:
            return default_enabled

        registry_entry = entity_registry.async_get(entity_id)
        if registry_entry is None:
            return default_enabled

        return not registry_entry.disabled

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
        _LOGGER.warning(
            "Unable to detect SNMP protocol for %s, defaulting to UPS-MIB", self.host
        )

    async def _try_protocol(
        self, protocol: str, oid_map: dict[str, dict[str, Any]], version: str
    ) -> bool:
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
        result = values.get(test_oid)
        return (
            result is not None and result.value is not None and not result.missing_oid
        )

    async def _fetch_keys(
        self, oid_map: dict[str, dict[str, Any]], keys: set[str]
    ) -> dict[str, Any]:
        """Fetch and normalize SNMP values for a set of keys."""
        oids: list[str] = []
        for key in keys:
            spec = oid_map.get(key)
            if not spec:
                continue
            for oid in self._spec_oids(spec):
                if oid in self._unsupported_oids:
                    continue
                if oid not in oids:
                    oids.append(oid)
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
            value: Any | None = None
            for oid in self._spec_oids(spec):
                if oid in self._unsupported_oids:
                    continue
                result = raw.get(oid)
                if result is None:
                    continue
                if result.missing_oid:
                    self._unsupported_oids.add(oid)
                    _LOGGER.debug(
                        "OID %s is not present on %s; skipping in future polls",
                        oid,
                        self.host,
                    )
                    continue
                value = self._coerce_snmp_value(result.value)
                break
            if value is None:
                continue
            if spec.get("timeticks_minutes"):
                value = round(value / 6000, 1)
            scale = spec.get("scale")
            if scale is not None and isinstance(value, (int, float)):
                value = round(value * scale, 2)
            data[key] = value

        return data

    @staticmethod
    def _spec_oids(spec: dict[str, Any]) -> list[str]:
        """Return one or more OIDs for a key spec, in priority order."""
        if "oids" in spec:
            return [str(oid) for oid in spec["oids"]]
        return [str(spec["oid"])]

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

        derived.update(
            {
                "output_source": output_source_text,
                "on_battery": on_battery,
                "ac_power": ac_power,
                "on_bypass": output_source_text == "bypass",
            }
        )

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
