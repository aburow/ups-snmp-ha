# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2026 Anthony Burow

"""Unified full sensor catalog for profile-level selection and picklists.

This module intentionally contains only static literals (no imports) so
external tools like ups2mqtt can consume it directly.

This catalog is exhaustive/selectable metadata and does not change unified
contract exposure or default-enabled behavior. Canonical `key` values are
authoritative; `aliases` provide alternate names only.

Category taxonomy (catalog metadata only):
- core: primary operational telemetry typically used for baseline monitoring.
- diagnostic: detailed status/fault/auxiliary telemetry for troubleshooting.
- config: device configuration or setpoint-style values.
- metadata: identity/capability/descriptive values, not live telemetry control.
- external: values sourced from external probes or out-of-band probe channels.

Category is classification metadata only and does not imply contract exposure,
default-enabled behavior, or profile membership semantics.

Note: `serial_number` is intentionally omitted from `ups_snmp_ups_mib` because
the current UPS-MIB profile has no static OID mapping for that key.
"""

ALL_SENSORS_UNIFIED = {
    "ups_snmp_ups_mib": {
        "profile_id": "ups_snmp_ups_mib",
        "protocol": "snmp",
        "sensors": [
            {
                "key": "output_source",
                "aliases": ["output_source_raw"],
                "label": "Output Source",
                "source": "derived",
                "oid": "1.3.6.1.2.1.33.1.4.1.0",
                "category": "core",
            },
            {
                "key": "runtime_remaining",
                "label": "Runtime Remaining",
                "source": "snmp",
                "oid": "1.3.6.1.2.1.33.1.2.3.0",
                "unit": "min",
                "category": "core",
            },
            {
                "key": "output_load",
                "label": "Output Load",
                "source": "snmp",
                "oid": "1.3.6.1.2.1.33.1.4.4.1.5.1",
                "unit": "%",
                "category": "core",
            },
            {
                "key": "seconds_on_battery",
                "label": "Seconds On Battery",
                "source": "snmp",
                "oid": "1.3.6.1.2.1.33.1.2.2.0",
                "unit": "s",
                "category": "core",
            },
            {
                "key": "battery_charge",
                "label": "Battery Charge",
                "source": "snmp",
                "oid": "1.3.6.1.2.1.33.1.2.4.0",
                "unit": "%",
                "category": "core",
            },
            {
                "key": "input_voltage",
                "label": "Input Voltage",
                "source": "snmp",
                "oid": "1.3.6.1.2.1.33.1.3.3.1.3.1",
                "unit": "V",
                "category": "core",
            },
            {
                "key": "ac_power",
                "label": "AC Power",
                "source": "derived",
                "category": "core",
            },
            {
                "key": "on_battery",
                "label": "On Battery",
                "source": "derived",
                "category": "core",
            },
            {
                "key": "on_bypass",
                "label": "On Bypass",
                "source": "derived",
                "category": "core",
            },
            {
                "key": "output_frequency",
                "label": "Output Frequency",
                "source": "snmp",
                "oid": "1.3.6.1.2.1.33.1.4.2.0",
                "unit": "Hz",
                "category": "diagnostic",
            },
            {
                "key": "output_line_count",
                "label": "Output Line Count",
                "source": "snmp",
                "oid": "1.3.6.1.2.1.33.1.4.3.0",
                "category": "diagnostic",
            },
            {
                "key": "battery_status",
                "aliases": ["battery_status_text"],
                "label": "Battery Status",
                "source": "snmp",
                "oid": "1.3.6.1.2.1.33.1.2.1.0",
                "category": "diagnostic",
            },
            {
                "key": "battery_temperature",
                "label": "Battery Temperature",
                "source": "snmp",
                "oid": "1.3.6.1.2.1.33.1.2.7.0",
                "unit": "°C",
                "category": "diagnostic",
            },
            {
                "key": "battery_voltage",
                "label": "Battery Voltage",
                "source": "snmp",
                "oid": "1.3.6.1.2.1.33.1.2.5.0",
                "unit": "V",
                "category": "diagnostic",
            },
            {
                "key": "alarms_present",
                "label": "Alarms Present",
                "source": "snmp",
                "oid": "1.3.6.1.2.1.33.1.6.1.0",
                "category": "diagnostic",
            },
            {
                "key": "bypass_frequency",
                "label": "Bypass Frequency",
                "source": "snmp",
                "oid": "1.3.6.1.2.1.33.1.5.1.0",
                "unit": "Hz",
                "category": "diagnostic",
            },
            {
                "key": "bypass_line_count",
                "label": "Bypass Line Count",
                "source": "snmp",
                "oid": "1.3.6.1.2.1.33.1.5.2.0",
                "category": "diagnostic",
            },
            {
                "key": "input_frequency",
                "label": "Input Frequency",
                "source": "snmp",
                "oid": "1.3.6.1.2.1.33.1.3.3.1.2.1",
                "unit": "Hz",
                "category": "diagnostic",
            },
            {
                "key": "input_line_count",
                "label": "Input Line Count",
                "source": "snmp",
                "oid": "1.3.6.1.2.1.33.1.3.2.0",
                "category": "diagnostic",
            },
            {
                "key": "input_current",
                "label": "Input Current",
                "source": "snmp",
                "oid": "1.3.6.1.2.1.33.1.3.3.1.4.1",
                "unit": "A",
                "category": "diagnostic",
            },
            {
                "key": "input_power",
                "label": "Input Power",
                "source": "snmp",
                "oid": "1.3.6.1.2.1.33.1.3.3.1.5.1",
                "category": "diagnostic",
            },
            {
                "key": "manufacturer",
                "label": "Manufacturer",
                "source": "snmp",
                "oid": "1.3.6.1.2.1.33.1.1.1.0",
                "category": "metadata",
            },
            {
                "key": "model",
                "label": "Model",
                "source": "snmp",
                "oid": "1.3.6.1.2.1.33.1.1.2.0",
                "category": "metadata",
            },
            {
                "key": "firmware",
                "aliases": ["sw_version"],
                "label": "Firmware",
                "source": "snmp",
                "oid": "1.3.6.1.2.1.33.1.1.3.0",
                "category": "metadata",
            },
            {
                "key": "name",
                "label": "Name",
                "source": "snmp",
                "oid": "1.3.6.1.2.1.33.1.1.5.0",
                "category": "metadata",
            },
        ],
    },
    "ups_snmp_apc_mib": {
        "profile_id": "ups_snmp_apc_mib",
        "protocol": "snmp",
        "sensors": [
            {
                "key": "output_source",
                "aliases": ["output_source_raw"],
                "label": "Output Source",
                "source": "derived",
                "oid": "1.3.6.1.4.1.318.1.1.1.4.1.1.0",
                "category": "core",
            },
            {
                "key": "runtime_remaining",
                "label": "Runtime Remaining",
                "source": "snmp",
                "oid": "1.3.6.1.4.1.318.1.1.1.2.2.3.0",
                "unit": "min",
                "category": "core",
            },
            {
                "key": "output_load",
                "label": "Output Load",
                "source": "snmp",
                "oid": "1.3.6.1.4.1.318.1.1.1.4.2.3.0",
                "unit": "%",
                "category": "core",
            },
            {
                "key": "battery_charge",
                "label": "Battery Charge",
                "source": "snmp",
                "oid": "1.3.6.1.4.1.318.1.1.1.2.2.1.0",
                "unit": "%",
                "category": "core",
            },
            {
                "key": "input_voltage",
                "label": "Input Voltage",
                "source": "snmp",
                "oid": "1.3.6.1.4.1.318.1.1.1.3.2.1.0",
                "unit": "V",
                "category": "core",
            },
            {
                "key": "ac_power",
                "label": "AC Power",
                "source": "derived",
                "category": "core",
            },
            {
                "key": "on_battery",
                "label": "On Battery",
                "source": "derived",
                "category": "core",
            },
            {
                "key": "on_bypass",
                "label": "On Bypass",
                "source": "derived",
                "category": "core",
            },
            {
                "key": "battery_status",
                "aliases": ["battery_status_text"],
                "label": "Battery Status",
                "source": "snmp",
                "oid": "1.3.6.1.4.1.318.1.1.1.2.1.1.0",
                "category": "diagnostic",
            },
            {
                "key": "battery_temperature",
                "label": "Battery Temperature",
                "source": "snmp",
                "oid": "1.3.6.1.4.1.318.1.1.1.2.2.2.0",
                "unit": "°C",
                "category": "diagnostic",
            },
            {
                "key": "output_voltage",
                "label": "Output Voltage",
                "source": "snmp",
                "oid": "1.3.6.1.4.1.318.1.1.1.4.2.1.0",
                "unit": "V",
                "category": "diagnostic",
            },
            {
                "key": "output_frequency",
                "label": "Output Frequency",
                "source": "snmp",
                "oid": "1.3.6.1.4.1.318.1.1.1.4.2.2.0",
                "unit": "Hz",
                "category": "diagnostic",
            },
            {
                "key": "input_frequency",
                "label": "Input Frequency",
                "source": "snmp",
                "oid": "1.3.6.1.4.1.318.1.1.1.3.2.4.0",
                "unit": "Hz",
                "category": "diagnostic",
            },
            {
                "key": "manufacturer",
                "label": "Manufacturer",
                "source": "derived",
                "category": "metadata",
            },
            {
                "key": "model",
                "label": "Model",
                "source": "snmp",
                "oid": "1.3.6.1.4.1.318.1.1.1.1.1.1.0",
                "category": "metadata",
            },
            {
                "key": "serial_number",
                "label": "Serial Number",
                "source": "snmp",
                "oid": "1.3.6.1.4.1.318.1.1.1.1.2.3.0",
                "category": "metadata",
            },
            {
                "key": "firmware",
                "aliases": ["sw_version"],
                "label": "Firmware",
                "source": "snmp",
                "oid": "1.3.6.1.4.1.318.1.1.1.1.2.1.0",
                "category": "metadata",
            },
            {
                "key": "name",
                "label": "Name",
                "source": "snmp",
                "oid": "1.3.6.1.4.1.318.1.1.1.1.1.2.0",
                "category": "metadata",
            },
        ],
    },
}
