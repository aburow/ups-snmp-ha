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
