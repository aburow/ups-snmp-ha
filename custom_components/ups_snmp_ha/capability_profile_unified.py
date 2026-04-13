# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2026 Anthony Burow
# https://github.com/aburow/ups-snmp-ha

"""UPS Unified capability profiles for SNMP polling.

This module is the bridge-facing contract surface for profile metadata and
poll-group definitions. Runtime coordinator logic can consume these structures
without changing SNMP transport behavior.
"""

from __future__ import annotations

from typing import Any

CONTRACT_VERSION = "2.0.0"

UPS_MIB = "ups_mib"
APC_MIB = "apc_mib"

DEFAULT_POLL_GROUP = "slow"

REQUIRED_PROFILE_KEYS = frozenset(
    {"manufacturer", "model", "serial_number", "firmware", "name"}
)
REQUIRED_DEPENDENCY_KEYS = frozenset({"output_source_raw"})

UPS_MIB_OIDS: dict[str, dict[str, Any]] = {
    "manufacturer": {"oid": "1.3.6.1.2.1.33.1.1.1.0"},
    "model": {"oid": "1.3.6.1.2.1.33.1.1.2.0"},
    "firmware": {"oid": "1.3.6.1.2.1.33.1.1.3.0"},
    "name": {"oid": "1.3.6.1.2.1.33.1.1.5.0"},
    "battery_status": {"oid": "1.3.6.1.2.1.33.1.2.1.0"},
    "seconds_on_battery": {"oid": "1.3.6.1.2.1.33.1.2.2.0", "poll_group": "fast"},
    "runtime_remaining": {"oid": "1.3.6.1.2.1.33.1.2.3.0", "poll_group": "fast"},
    "battery_charge": {"oid": "1.3.6.1.2.1.33.1.2.4.0", "poll_group": "fast"},
    "battery_voltage": {"oid": "1.3.6.1.2.1.33.1.2.5.0", "scale": 0.1},
    "battery_temperature": {"oid": "1.3.6.1.2.1.33.1.2.7.0"},
    "input_line_count": {"oid": "1.3.6.1.2.1.33.1.3.2.0"},
    "input_frequency": {"oid": "1.3.6.1.2.1.33.1.3.3.1.2.1", "scale": 0.1},
    "input_voltage": {"oid": "1.3.6.1.2.1.33.1.3.3.1.3.1", "poll_group": "fast"},
    "input_current": {"oid": "1.3.6.1.2.1.33.1.3.3.1.4.1", "scale": 0.1},
    "input_power": {"oid": "1.3.6.1.2.1.33.1.3.3.1.5.1"},
    "output_source_raw": {"oid": "1.3.6.1.2.1.33.1.4.1.0", "poll_group": "fast"},
    "output_frequency": {"oid": "1.3.6.1.2.1.33.1.4.2.0", "scale": 0.1},
    "output_line_count": {"oid": "1.3.6.1.2.1.33.1.4.3.0"},
    "output_load": {
        "oids": ["1.3.6.1.2.1.33.1.4.4.1.5.1", "1.3.6.1.2.1.33.1.4.4.1.5.0"],
        "poll_group": "fast",
    },
    "bypass_frequency": {"oid": "1.3.6.1.2.1.33.1.5.1.0", "scale": 0.1},
    "bypass_line_count": {"oid": "1.3.6.1.2.1.33.1.5.2.0"},
    "alarms_present": {"oid": "1.3.6.1.2.1.33.1.6.1.0"},
}

APC_MIB_OIDS: dict[str, dict[str, Any]] = {
    "model": {"oid": "1.3.6.1.4.1.318.1.1.1.1.1.1.0"},
    "name": {"oid": "1.3.6.1.4.1.318.1.1.1.1.1.2.0"},
    "firmware": {"oid": "1.3.6.1.4.1.318.1.1.1.1.2.1.0"},
    "serial_number": {"oid": "1.3.6.1.4.1.318.1.1.1.1.2.3.0"},
    "battery_status": {"oid": "1.3.6.1.4.1.318.1.1.1.2.1.1.0"},
    "battery_charge": {"oid": "1.3.6.1.4.1.318.1.1.1.2.2.1.0", "poll_group": "fast"},
    "battery_temperature": {"oid": "1.3.6.1.4.1.318.1.1.1.2.2.2.0"},
    "runtime_remaining": {
        "oid": "1.3.6.1.4.1.318.1.1.1.2.2.3.0",
        "timeticks_minutes": True,
        "poll_group": "fast",
    },
    "output_source_raw": {"oid": "1.3.6.1.4.1.318.1.1.1.4.1.1.0", "poll_group": "fast"},
    "output_voltage": {"oid": "1.3.6.1.4.1.318.1.1.1.4.2.1.0"},
    "output_frequency": {"oid": "1.3.6.1.4.1.318.1.1.1.4.2.2.0"},
    "output_load": {"oid": "1.3.6.1.4.1.318.1.1.1.4.2.3.0", "poll_group": "fast"},
    "input_voltage": {"oid": "1.3.6.1.4.1.318.1.1.1.3.2.1.0", "poll_group": "fast"},
    "input_frequency": {"oid": "1.3.6.1.4.1.318.1.1.1.3.2.4.0"},
}

UPS_MIB_PROFILE: dict[str, Any] = {
    "profile_id": "ups_snmp_ups_mib",
    "protocol": "snmp",
    "oids": UPS_MIB_OIDS,
    "snmp_blocks": [
        {
            "name": "core_fast",
            "metrics": [
                "output_source_raw",
                "runtime_remaining",
                "output_load",
                "seconds_on_battery",
                "battery_charge",
                "input_voltage",
            ],
            "poll_group": "fast",
        }
    ],
    "poll_groups": {"fast": {"interval_s": 10}, "slow": {"interval_s": 60}},
}

APC_MIB_PROFILE: dict[str, Any] = {
    "profile_id": "ups_snmp_apc_mib",
    "protocol": "snmp",
    "oids": APC_MIB_OIDS,
    "snmp_blocks": [
        {
            "name": "core_fast",
            "metrics": [
                "output_source_raw",
                "runtime_remaining",
                "output_load",
                "battery_charge",
                "input_voltage",
            ],
            "poll_group": "fast",
        }
    ],
    "poll_groups": {"fast": {"interval_s": 10}, "slow": {"interval_s": 60}},
}

CAPABILITY_PROFILES: dict[str, dict[str, Any]] = {
    UPS_MIB: UPS_MIB_PROFILE,
    APC_MIB: APC_MIB_PROFILE,
}

CAPABILITY_SOURCE: dict[str, Any] = {
    "contract_version": CONTRACT_VERSION,
    "profiles": CAPABILITY_PROFILES,
}


def fast_poll_keys_for(protocol_key: str) -> frozenset[str]:
    """Return fast-lane metric keys for a given profile key."""
    profile = CAPABILITY_PROFILES.get(protocol_key)
    if not profile:
        return frozenset()
    oids = profile.get("oids", {})
    if not isinstance(oids, dict):
        return frozenset()
    return frozenset(
        key
        for key, spec in oids.items()
        if isinstance(spec, dict) and spec.get("poll_group", DEFAULT_POLL_GROUP) == "fast"
    )


def validate_capability_profiles() -> list[str]:
    """Validate local capability profiles against UPS Unified v2 constraints."""
    errors: list[str] = []
    for profile_key, profile in CAPABILITY_PROFILES.items():
        protocol = profile.get("protocol")
        if protocol != "snmp":
            errors.append(f"{profile_key}: protocol must be 'snmp'")

        oids = profile.get("oids")
        if not isinstance(oids, dict):
            errors.append(f"{profile_key}: missing oids mapping")
            continue

        metric_keys = list(oids.keys())
        if len(metric_keys) != len(set(metric_keys)):
            errors.append(f"{profile_key}: duplicate metric keys in oids")

        poll_groups = profile.get("poll_groups", {})
        if not isinstance(poll_groups, dict):
            errors.append(f"{profile_key}: poll_groups must be a mapping")
            poll_groups = {}
        if DEFAULT_POLL_GROUP not in poll_groups:
            errors.append(f"{profile_key}: missing default poll group '{DEFAULT_POLL_GROUP}'")

        for metric_key, spec in oids.items():
            if not isinstance(spec, dict):
                errors.append(f"{profile_key}.{metric_key}: spec must be a mapping")
                continue
            if "oid" not in spec and "oids" not in spec:
                errors.append(f"{profile_key}.{metric_key}: must define 'oid' or 'oids'")
            group = spec.get("poll_group", DEFAULT_POLL_GROUP)
            if group not in poll_groups:
                errors.append(
                    f"{profile_key}.{metric_key}: poll_group '{group}' missing in poll_groups"
                )

        blocks = profile.get("snmp_blocks", [])
        if not isinstance(blocks, list):
            errors.append(f"{profile_key}: snmp_blocks must be a list")
            continue
        for block in blocks:
            if not isinstance(block, dict):
                errors.append(f"{profile_key}: block must be a mapping")
                continue
            group = block.get("poll_group", DEFAULT_POLL_GROUP)
            if group not in poll_groups:
                errors.append(
                    f"{profile_key}.{block.get('name', 'block')}: poll_group '{group}' missing in poll_groups"
                )
            metrics = block.get("metrics", [])
            if not isinstance(metrics, list):
                errors.append(
                    f"{profile_key}.{block.get('name', 'block')}: metrics must be a list"
                )
                continue
            for metric in metrics:
                if metric not in oids:
                    errors.append(
                        f"{profile_key}.{block.get('name', 'block')}: unknown metric '{metric}'"
                    )

    return errors
