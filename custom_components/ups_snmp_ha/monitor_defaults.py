# SPDX-License-Identifier: GPL-3.0
# Copyright (C) 2026 Anthony Burow
# https://github.com/aburow/ups-snmp-ha

"""Helpers to reset entity enablement to integration defaults."""

from __future__ import annotations

from collections.abc import Iterable

from homeassistant.helpers import entity_registry as er

from .const import DOMAIN
from .sensor_availability_unified import entity_enabled_default

SUPPORTED_ENTITY_DOMAINS = frozenset({"sensor", "binary_sensor"})


def _extract_local_key(entry_id: str, unique_id: str | None) -> str | None:
    """Extract local entity key from this integration's unique_id pattern."""
    if not unique_id:
        return None
    prefix = f"{DOMAIN}_{entry_id}_"
    if not unique_id.startswith(prefix):
        return None
    return unique_id[len(prefix) :]


async def async_reset_monitor_defaults(
    hass, entry_ids: Iterable[str]
) -> dict[str, int]:
    """Reset enabled/disabled state to integration defaults.

    Returns summary dict with number of changed entities.
    """
    entity_registry = er.async_get(hass)
    changed = 0
    processed = 0

    for entry_id in entry_ids:
        for registry_entry in er.async_entries_for_config_entry(entity_registry, entry_id):
            if registry_entry.domain not in SUPPORTED_ENTITY_DOMAINS:
                continue
            local_key = _extract_local_key(entry_id, registry_entry.unique_id)
            if local_key is None:
                continue

            should_enable = entity_enabled_default(local_key)
            desired_disabled_by = (
                None if should_enable else er.RegistryEntryDisabler.INTEGRATION
            )
            processed += 1
            if registry_entry.disabled_by == desired_disabled_by:
                continue

            entity_registry.async_update_entity(
                registry_entry.entity_id,
                disabled_by=desired_disabled_by,
            )
            changed += 1

    return {"processed": processed, "changed": changed}
