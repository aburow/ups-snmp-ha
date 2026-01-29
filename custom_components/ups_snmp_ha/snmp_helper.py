# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2026 Anthony Burow
# https://github.com/aburow/ups-snmp-ha

"""SNMP helper utilities for UPS polling."""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

from pysnmp.hlapi.v3arch.asyncio import (
    CommunityData,
    ContextData,
    ObjectIdentity,
    ObjectType,
    SnmpEngine,
    UdpTransportTarget,
    get_cmd,
)
from pysnmp.proto.rfc1902 import Null
from pysnmp.proto.rfc1905 import EndOfMibView, NoSuchInstance, NoSuchObject

_LOGGER = logging.getLogger(__name__)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


def _snmp_version_to_model(version: str) -> int:
    """Map SNMP version string to pysnmp mpModel."""
    return 0 if version == "1" else 1


def _is_missing_value(value: object) -> bool:
    """Return True if pysnmp returned a missing/invalid value."""
    if isinstance(value, Null):
        return True
    if not hasattr(value, "isSameTypeWith"):
        return False
    if value.isSameTypeWith(Null()):
        return True
    if value.isSameTypeWith(NoSuchInstance()):
        return True
    if value.isSameTypeWith(NoSuchObject()):
        return True
    if value.isSameTypeWith(EndOfMibView()):
        return True
    return False


async def _async_get_snmp_value(
    host: str,
    oid: str,
    community: str = "public",
    timeout: int = 5,
    version: str = "2c",
) -> str | None:
    """Query single SNMP OID and return string value."""
    try:
        _LOGGER.debug("SNMP query to %s OID %s (timeout=%ds)", host, oid, timeout)

        target = await UdpTransportTarget.create((host, 161), timeout=timeout, retries=3)

        error_indication, error_status, error_index, var_binds = await get_cmd(
            SnmpEngine(),
            CommunityData(community, mpModel=_snmp_version_to_model(version)),
            target,
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
        )

        if error_indication:
            _LOGGER.debug("SNMP error from %s (OID %s): %s", host, oid, error_indication)
            return None
        if error_status:
            _LOGGER.debug(
                "SNMP error status from %s (OID %s): %s at index %s",
                host,
                oid,
                error_status.prettyPrint(),
                error_index,
            )
            return None

        for var_bind in var_binds:
            value_obj = var_bind[1]
            if _is_missing_value(value_obj):
                _LOGGER.debug("SNMP query returned missing value for OID %s", oid)
                return None
            value = str(value_obj).strip()
            if not value:
                _LOGGER.debug("SNMP query returned empty value for OID %s", oid)
                return None
            _LOGGER.debug("SNMP query succeeded: %s=%s", oid, value[:50] if len(value) > 50 else value)
            return value

        _LOGGER.debug("SNMP query returned no value for OID %s", oid)
        return None

    except asyncio.TimeoutError:
        _LOGGER.warning("SNMP query to %s timed out after %ds for OID %s", host, timeout, oid)
        return None
    except Exception as err:
        _LOGGER.debug("SNMP query failed for %s (OID %s): %s (%s)", host, oid, err, type(err).__name__)
        return None


async def _async_get_snmp_values(
    host: str,
    oids: list[str],
    community: str = "public",
    timeout: int = 5,
    version: str = "2c",
) -> dict[str, str | None]:
    """Query multiple SNMP OIDs using individual GETs to match HA loop expectations."""
    if not oids:
        return {}

    results = await asyncio.gather(
        *[_async_get_snmp_value(host, oid, community, timeout, version) for oid in oids],
        return_exceptions=True,
    )

    values: dict[str, str | None] = {}
    for oid, result in zip(oids, results, strict=True):
        if isinstance(result, Exception):
            values[oid] = None
        else:
            values[oid] = result

    return values


def _get_snmp_values_sync(
    host: str,
    oids: list[str],
    community: str,
    timeout: int,
    version: str,
) -> dict[str, str | None]:
    """Run SNMP queries in a dedicated thread to avoid blocking the HA event loop."""
    return asyncio.run(_async_get_snmp_values(host, oids, community, timeout, version))


async def async_get_snmp_values(
    host: str,
    oids: list[str],
    community: str = "public",
    timeout: int = 5,
    version: str = "2c",
    hass: HomeAssistant | None = None,
    use_executor: bool = True,
) -> dict[str, str | None]:
    """Query multiple SNMP OIDs, optionally offloading to an executor."""
    if not oids:
        return {}

    if use_executor:
        if hass is None:
            raise RuntimeError("Home Assistant instance required for executor SNMP calls")
        return await hass.async_add_executor_job(
            _get_snmp_values_sync, host, oids, community, timeout, version
        )

    return await _async_get_snmp_values(host, oids, community, timeout, version)
