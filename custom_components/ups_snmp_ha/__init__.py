# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2026 Anthony Burow
# https://github.com/aburow/ups-snmp-ha

"""UPS SNMP integration entry point."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import (
    CONF_DEVICE_NAME,
    CONF_FAST_POLL_INTERVAL,
    CONF_SLOW_POLL_INTERVAL,
    CONF_SNMP_COMMUNITY,
    DEFAULT_FAST_POLL_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_SLOW_POLL_INTERVAL,
    DEFAULT_SNMP_COMMUNITY,
    DOMAIN,
    KEY_COORDINATOR,
    SUPPORTED_PLATFORMS,
)
from .coordinator import UpsSnmpCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up UPS SNMP from a config entry."""
    _LOGGER.info("UPS SNMP integration starting")
    hass.data.setdefault(DOMAIN, {})

    host = entry.data[CONF_HOST]
    device_name = entry.data.get(CONF_DEVICE_NAME, DEFAULT_NAME)
    snmp_community = entry.data.get(CONF_SNMP_COMMUNITY, DEFAULT_SNMP_COMMUNITY)
    fast_poll = entry.data.get(CONF_FAST_POLL_INTERVAL, DEFAULT_FAST_POLL_INTERVAL)
    slow_poll = entry.data.get(CONF_SLOW_POLL_INTERVAL, DEFAULT_SLOW_POLL_INTERVAL)

    coordinator = UpsSnmpCoordinator(
        hass=hass,
        host=host,
        community=snmp_community,
        device_name=device_name,
        fast_poll_interval=fast_poll,
        slow_poll_interval=slow_poll,
        entry_id=entry.entry_id,
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        _LOGGER.error("Failed to fetch initial SNMP data from %s: %s", host, err)
        raise ConfigEntryNotReady(f"Failed to fetch initial data: {err}") from err

    hass.data[DOMAIN][entry.entry_id] = {
        KEY_COORDINATOR: coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, SUPPORTED_PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a UPS SNMP config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, SUPPORTED_PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
