# SPDX-License-Identifier: AGPL-3.0-or-later

"""Tests for the Home Assistant integration manifest."""

import json
from pathlib import Path


MANIFEST_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "ups_snmp_ha"
    / "manifest.json"
)


def test_manifest_declares_home_assistant_snmp_dependency() -> None:
    """Ensure PySNMP is installed before this integration is imported."""
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    assert "snmp" in manifest["dependencies"]
    assert manifest["requirements"] == []
