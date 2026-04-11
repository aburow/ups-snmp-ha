# SPDX-FileCopyrightText: 2026 github.com/aburow
# SPDX-License-Identifier: GPL-3.0-only

"""Unified availability defaults for UPS metrics.

This module is dependency-free and framework-independent by design.
It provides canonical metric naming and core/default-enabled membership.
"""

from __future__ import annotations


# Canonical metrics enabled by default across UPS projects.
CANONICAL_CORE_METRICS: frozenset[str] = frozenset(
    {
        "output_source",
        "runtime_remaining",
        "output_load",
        "seconds_on_battery",
        "battery_charge",
        "input_voltage",
        "ac_power",
        "on_battery",
        "on_bypass",
    }
)


# Local adapter: UPS SNMP keys -> canonical metrics.
LOCAL_TO_CANONICAL_METRIC: dict[str, str] = {
    "ac_power": "ac_power",
    "alarms_present": "alarms_present",
    "battery_charge": "battery_charge",
    "battery_status": "battery_status",
    "battery_status_text": "battery_status",
    "battery_temperature": "battery_temperature",
    "battery_voltage": "battery_voltage",
    "bypass_frequency": "bypass_frequency",
    "bypass_line_count": "bypass_line_count",
    "firmware": "firmware",
    "input_frequency": "input_frequency",
    "input_line_count": "input_line_count",
    "input_voltage": "input_voltage",
    "manufacturer": "manufacturer",
    "model": "model",
    "name": "name",
    "on_battery": "on_battery",
    "on_bypass": "on_bypass",
    "output_frequency": "output_frequency",
    "output_line_count": "output_line_count",
    "output_load": "output_load",
    "output_source": "output_source",
    "output_source_raw": "output_source",
    "runtime_remaining": "runtime_remaining",
    "seconds_on_battery": "seconds_on_battery",
    "serial_number": "serial_number",
}


def resolve_canonical_metric(local_key: str) -> str | None:
    """Return canonical metric id for a local project key."""
    return LOCAL_TO_CANONICAL_METRIC.get(local_key)


def is_core_canonical_metric(metric: str | None) -> bool:
    """Return whether a canonical metric is core/default-enabled."""
    return metric in CANONICAL_CORE_METRICS


def is_core_local_metric(local_key: str) -> bool:
    """Return whether a local key maps to a core/default-enabled metric."""
    return is_core_canonical_metric(resolve_canonical_metric(local_key))


def entity_enabled_default(local_entity_key: str) -> bool:
    """Return default entity-registry enabled state for a local entity key."""
    return is_core_local_metric(local_entity_key)
