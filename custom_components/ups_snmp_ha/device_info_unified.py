# SPDX-FileCopyrightText: 2026 github.com/aburow
# SPDX-License-Identifier: GPL-3.0-only

"""Unified device metadata resolver for external bridge consumers.

This module is dependency-free and import-safe outside Home Assistant.
"""

from __future__ import annotations

from typing import Any

CONTRACT_VERSION = "1.0"

_CANONICAL_KEYS = frozenset(
    {
        "manufacturer",
        "model",
        "sw_version",
        "hw_version",
        "serial_number",
        "configuration_url",
    }
)

_SUPPORTED_SOURCES = frozenset(
    {
        "ups_snmp",
        "ups_snmp_ups_mib",
        "ups_snmp_apc_mib",
        "ups_mib",
        "apc_mib",
    }
)

_UNKNOWN_MARKERS = frozenset({"unknown", "none", "null", "n/a", "na"})


def _normalize_text(value: Any) -> str | None:
    """Normalize a metadata value to a trimmed non-empty string."""
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
    elif isinstance(value, (int, float, bool)):
        text = str(value).strip()
    else:
        return None
    if not text:
        return None
    if text.lower() in _UNKNOWN_MARKERS:
        return None
    return text


def _source_supported(source: Any) -> bool:
    """Return True if a source profile is supported by this integration."""
    source_text = _normalize_text(source)
    if source_text is None:
        return False
    return source_text.lower() in _SUPPORTED_SOURCES


def _valid_configuration_url(url_text: str | None) -> str | None:
    """Return URL only when it is an absolute HTTP(S) URL."""
    if not url_text:
        return None
    lowered = url_text.lower()
    if lowered.startswith("http://") or lowered.startswith("https://"):
        return url_text
    return None


def resolve_device_info(values: dict[str, Any], source: str) -> dict[str, str]:
    """Return canonical device info fields for MQTT discovery device block."""
    if not _source_supported(source):
        return {}
    if not isinstance(values, dict):
        return {}

    result: dict[str, str] = {}

    manufacturer = _normalize_text(values.get("manufacturer"))
    if manufacturer:
        result["manufacturer"] = manufacturer

    model = _normalize_text(values.get("model"))
    if model:
        result["model"] = model

    sw_version = _normalize_text(values.get("sw_version"))
    if not sw_version:
        sw_version = _normalize_text(values.get("firmware"))
    if sw_version:
        result["sw_version"] = sw_version

    hw_version = _normalize_text(values.get("hw_version"))
    if not hw_version:
        hw_version = _normalize_text(values.get("hardware_version"))
    if hw_version:
        result["hw_version"] = hw_version

    serial_number = _normalize_text(values.get("serial_number"))
    if serial_number:
        result["serial_number"] = serial_number

    configuration_url = _normalize_text(values.get("configuration_url"))
    if not configuration_url:
        configuration_url = _normalize_text(values.get("url"))
    if not configuration_url:
        configuration_url = _normalize_text(values.get("web_url"))
    configuration_url = _valid_configuration_url(configuration_url)
    if configuration_url:
        result["configuration_url"] = configuration_url

    if not set(result).issubset(_CANONICAL_KEYS):
        return {}

    return result
