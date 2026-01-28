# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2026 Anthony Burow
# https://github.com/aburow/ups-snmp-ha

"""Sensor platform for UPS data."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    UpsSnmpSensorDescription,
    DOMAIN,
    KEY_COORDINATOR,
    SNMP_SENSOR_DESCRIPTIONS,
)
from .coordinator import UpsSnmpCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the UPS sensors for a config entry."""
    coordinator: UpsSnmpCoordinator = hass.data[DOMAIN][entry.entry_id][KEY_COORDINATOR]
    sensor_descriptions = SNMP_SENSOR_DESCRIPTIONS
    _LOGGER.debug("Setting up %d SNMP sensors", len(sensor_descriptions))

    async_add_entities(
        UpsSnmpSensor(coordinator, description, entry.entry_id) for description in sensor_descriptions
    )


class UpsSnmpSensor(CoordinatorEntity, SensorEntity):
    """Representation of a UPS SNMP sensor."""

    has_entity_name = True

    def __init__(self, coordinator: UpsSnmpCoordinator, description: UpsSnmpSensorDescription, entry_id: str) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=coordinator.device_name,
            manufacturer=coordinator.manufacturer or "UPS",
            model=coordinator.hw_model or "UPS",
            serial_number=coordinator.serial_number,
            sw_version=coordinator.fw_version,
        )

    @property
    def native_value(self):
        """Return the latest value from the coordinator."""
        return self.coordinator.data.get(self.entity_description.data_key)
