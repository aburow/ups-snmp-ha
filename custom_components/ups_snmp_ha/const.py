# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2026 Anthony Burow
# https://github.com/aburow/ups-snmp-ha

"""Constants for the UPS SNMP integration."""

from dataclasses import dataclass
from datetime import timedelta

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntityDescription,
)
from homeassistant.components.sensor import SensorEntityDescription, SensorStateClass

DOMAIN = "ups_snmp_ha"
DEFAULT_NAME = "UPS"
DEFAULT_SNMP_COMMUNITY = "public"
DEFAULT_FAST_POLL_INTERVAL = 10
DEFAULT_SLOW_POLL_INTERVAL = 300

CONF_DEVICE_NAME = "device_name"
CONF_SNMP_COMMUNITY = "snmp_community"
CONF_FAST_POLL_INTERVAL = "fast_poll_interval"
CONF_SLOW_POLL_INTERVAL = "slow_poll_interval"

KEY_COORDINATOR = "coordinator"

SUPPORTED_PLATFORMS = ["sensor", "binary_sensor"]


@dataclass
class UpsSnmpSensorDescription(SensorEntityDescription):
    """Describe a UPS SNMP sensor."""

    data_key: str = ""


@dataclass
class UpsSnmpBinarySensorDescription(BinarySensorEntityDescription):
    """Describe a UPS SNMP binary sensor."""

    data_key: str = ""


FAST_POLL_INTERVAL = timedelta(seconds=DEFAULT_FAST_POLL_INTERVAL)
SLOW_POLL_INTERVAL = timedelta(seconds=DEFAULT_SLOW_POLL_INTERVAL)

_SENSOR_ICON_PATTERNS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("temperature", "temp"), "mdi:thermometer"),
    (("humidity",), "mdi:water-percent"),
    (("voltage",), "mdi:sine-wave"),
    (("current", "amperage", "amps"), "mdi:current-ac"),
    (("power",), "mdi:power-plug"),
    (("energy",), "mdi:lightning-bolt"),
    (("runtime", "seconds_on_battery"), "mdi:timer-outline"),
    (("load",), "mdi:gauge"),
    (("state", "status", "source"), "mdi:information-outline"),
    (("battery_charge", "state_of_charge"), "mdi:battery"),
    (("battery",), "mdi:battery-medium"),
    (("frequency",), "mdi:sine-wave"),
    (("line_count", "phase_count"), "mdi:transmission-tower"),
    (("alarm", "fault"), "mdi:alert-circle-outline"),
)

_BINARY_SENSOR_ICON_PATTERNS: tuple[tuple[tuple[str, ...], str, str], ...] = (
    (("fault", "alarm"), "mdi:alert-circle-outline", "mdi:check-circle-outline"),
    (("overload",), "mdi:alert-octagon", "mdi:check-circle-outline"),
    (("on_battery", "battery"), "mdi:battery-alert", "mdi:battery-check"),
    (("on_bypass", "bypass"), "mdi:transit-detour", "mdi:check-circle-outline"),
    (("online", "ac_power", "mains"), "mdi:power-plug", "mdi:power-plug-off"),
    (("output_off", "output_disabled"), "mdi:power", "mdi:power-off"),
)

SNMP_SENSOR_DESCRIPTIONS = [
    UpsSnmpSensorDescription(
        key="output_source",
        name="Output Source",
        data_key="output_source",
        state_class=None,
    ),
    UpsSnmpSensorDescription(
        key="runtime_remaining",
        name="Runtime Remaining",
        native_unit_of_measurement="min",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="runtime_remaining",
    ),
    UpsSnmpSensorDescription(
        key="alarms_present",
        name="Alarms Present",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="alarms_present",
    ),
    UpsSnmpSensorDescription(
        key="battery_charge",
        name="Battery Charge",
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="battery_charge",
    ),
    UpsSnmpSensorDescription(
        key="battery_status",
        name="Battery Status",
        data_key="battery_status_text",
        state_class=None,
    ),
    UpsSnmpSensorDescription(
        key="battery_temperature",
        name="Battery Temperature",
        native_unit_of_measurement="°C",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="battery_temperature",
    ),
    UpsSnmpSensorDescription(
        key="battery_voltage",
        name="Battery Voltage",
        native_unit_of_measurement="V",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="battery_voltage",
    ),
    UpsSnmpSensorDescription(
        key="bypass_frequency",
        name="Bypass Frequency",
        native_unit_of_measurement="Hz",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="bypass_frequency",
    ),
    UpsSnmpSensorDescription(
        key="bypass_line_count",
        name="Bypass Line Count",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="bypass_line_count",
    ),
    UpsSnmpSensorDescription(
        key="input_frequency",
        name="Input Frequency",
        native_unit_of_measurement="Hz",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="input_frequency",
    ),
    UpsSnmpSensorDescription(
        key="input_line_count",
        name="Input Line Count",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="input_line_count",
    ),
    UpsSnmpSensorDescription(
        key="input_voltage",
        name="Input Voltage",
        native_unit_of_measurement="V",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="input_voltage",
    ),
    UpsSnmpSensorDescription(
        key="output_frequency",
        name="Output Frequency",
        native_unit_of_measurement="Hz",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="output_frequency",
    ),
    UpsSnmpSensorDescription(
        key="output_line_count",
        name="Output Line Count",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="output_line_count",
    ),
    UpsSnmpSensorDescription(
        key="output_load",
        name="Output Load",
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="output_load",
    ),
    UpsSnmpSensorDescription(
        key="seconds_on_battery",
        name="Seconds On Battery",
        native_unit_of_measurement="s",
        state_class=SensorStateClass.MEASUREMENT,
        data_key="seconds_on_battery",
    ),
]

SNMP_BINARY_SENSOR_DESCRIPTIONS = [
    UpsSnmpBinarySensorDescription(
        key="ac_power",
        name="AC Power",
        device_class=BinarySensorDeviceClass.POWER,
        data_key="ac_power",
    ),
    UpsSnmpBinarySensorDescription(
        key="on_battery",
        name="On Battery",
        device_class=BinarySensorDeviceClass.BATTERY,
        data_key="on_battery",
    ),
    UpsSnmpBinarySensorDescription(
        key="on_bypass",
        name="On Bypass",
        device_class=BinarySensorDeviceClass.POWER,
        data_key="on_bypass",
    ),
]


def _matches_pattern(value: str, patterns: tuple[str, ...]) -> bool:
    """Return true when the key/value token contains any icon pattern."""
    return any(pattern in value for pattern in patterns)


def sensor_icon_for_key(*keys: str | None) -> str:
    """Resolve a deterministic mdi icon from sensor key patterns."""
    lookup_value = "_".join(part.lower() for part in keys if part)
    for patterns, icon in _SENSOR_ICON_PATTERNS:
        if _matches_pattern(lookup_value, patterns):
            return icon
    return "mdi:gauge"


def binary_sensor_icon_for_key(is_on: bool | None, *keys: str | None) -> str:
    """Resolve deterministic mdi icons for binary sensors by semantic patterns."""
    lookup_value = "_".join(part.lower() for part in keys if part)
    for patterns, on_icon, off_icon in _BINARY_SENSOR_ICON_PATTERNS:
        if _matches_pattern(lookup_value, patterns):
            return on_icon if is_on else off_icon
    return (
        "mdi:checkbox-marked-circle-outline"
        if is_on
        else "mdi:checkbox-blank-circle-outline"
    )
