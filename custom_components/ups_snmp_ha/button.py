# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2026 Anthony Burow
# https://github.com/aburow/ups-snmp-ha

"""Button platform for UPS SNMP actions."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, KEY_COORDINATOR
from .coordinator import UpsSnmpCoordinator
from .monitor_defaults import async_reset_monitor_defaults

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up UPS SNMP button entities for a config entry."""
    coordinator: UpsSnmpCoordinator = hass.data[DOMAIN][entry.entry_id][KEY_COORDINATOR]
    async_add_entities([UpsSnmpResetMonitorsButton(coordinator, entry.entry_id)])


class UpsSnmpResetMonitorsButton(CoordinatorEntity, ButtonEntity):
    """Button that resets monitor enablement to integration defaults."""

    has_entity_name = True
    _attr_name = "Reset Monitors"
    _attr_icon = "mdi:restart-alert"

    def __init__(self, coordinator: UpsSnmpCoordinator, entry_id: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_reset_monitors"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=coordinator.device_name,
            manufacturer=coordinator.manufacturer or "UPS",
            model=coordinator.hw_model or "UPS",
            serial_number=coordinator.serial_number,
            sw_version=coordinator.fw_version,
        )

    async def async_press(self) -> None:
        """Reset entity defaults for this UPS entry."""
        summary = await async_reset_monitor_defaults(self.hass, [self._entry_id])
        _LOGGER.info(
            "Reset monitor defaults for entry_id=%s (processed=%d changed=%d)",
            self._entry_id,
            summary["processed"],
            summary["changed"],
        )
