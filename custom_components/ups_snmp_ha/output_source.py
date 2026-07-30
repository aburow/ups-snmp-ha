# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Anthony Burow

"""Normalize SNMP UPS output-source values into Home Assistant states."""

from __future__ import annotations

from typing import Any


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
    2: "online",
    3: "battery",
    4: "smart_boost",
    5: "timed_sleeping",
    6: "software_bypass",
    7: "off",
    8: "rebooting",
    9: "switched_bypass",
    10: "hardware_failure_bypass",
    11: "sleeping_until_power_return",
    12: "smart_trim",
    13: "eco_mode",
    14: "hot_standby",
    15: "battery_test",
    16: "emergency_static_bypass",
    17: "static_bypass_standby",
    18: "power_saving_mode",
    19: "spot_mode",
    20: "e_conversion",
    21: "charger_spot_mode",
    22: "inverter_spot_mode",
    23: "active_load",
    24: "battery_discharge_spot_mode",
    25: "inverter_standby",
    26: "charger_only",
    27: "distributed_energy_reserve",
    28: "self_test",
}

APC_AC_ON_VALUES = {2, 4, 6, 9, 10, 12, 13, 16, 20, 23}
APC_AC_OFF_VALUES = {3, 5, 7, 8, 11, 15, 24, 26}
APC_BATTERY_VALUES = {3, 15, 24, 27}
APC_BYPASS_VALUES = {6, 9, 10, 16, 17}

UPS_TEST_STATUS_MAP = {
    1: "done_pass",
    2: "done_warning",
    3: "done_error",
    4: "aborted",
    5: "in_progress",
    6: "no_tests_initiated",
}

APC_CALIBRATION_STATUS_MAP = {
    1: "ok",
    2: "invalid_calibration",
    3: "calibration_in_progress",
    4: "refused",
    5: "aborted",
    6: "pending",
}


def derive_output_states(protocol: str, raw_value: Any) -> dict[str, Any]:
    """Derive output-source and binary states from an SNMP enum value."""
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return {
            "output_source": "unknown",
            "on_battery": None,
            "ac_power": None,
            "on_bypass": None,
        }

    if protocol == "apc_mib":
        source_map = APC_OUTPUT_SOURCE_MAP
        ac_on_values = APC_AC_ON_VALUES
        ac_off_values = APC_AC_OFF_VALUES
        battery_values = APC_BATTERY_VALUES
        bypass_values = APC_BYPASS_VALUES
    else:
        source_map = UPS_OUTPUT_SOURCE_MAP
        ac_on_values = {3, 4, 6, 7}
        ac_off_values = {2, 5}
        battery_values = {5}
        bypass_values = {4}

    output_source = source_map.get(value, "unknown")
    is_known = value in source_map and output_source != "other"

    if value in ac_on_values:
        ac_power = True
    elif value in ac_off_values:
        ac_power = False
    else:
        ac_power = None

    return {
        "output_source": output_source,
        "on_battery": value in battery_values if is_known else None,
        "ac_power": ac_power,
        "on_bypass": value in bypass_values if is_known else None,
    }


def derive_test_status(protocol: str, raw_value: Any) -> str:
    """Return a readable RFC 1628 test or APC calibration status."""
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return "unknown"
    status_map = (
        APC_CALIBRATION_STATUS_MAP if protocol == "apc_mib" else UPS_TEST_STATUS_MAP
    )
    return status_map.get(value, "unknown")
