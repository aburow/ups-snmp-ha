"""Acceptance tests for UPS Unified interop contract v2."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

BASE_DIR = Path(__file__).resolve().parents[1] / "custom_components" / "ups_snmp_ha"
ICONS_PATH = BASE_DIR / "icons_unified.py"
AVAILABILITY_PATH = BASE_DIR / "sensor_availability_unified.py"
DEVICE_INFO_PATH = BASE_DIR / "device_info_unified.py"
PROFILES_PATH = BASE_DIR / "capability_profile_unified.py"

ALLOWED_DEVICE_INFO_KEYS = {
    "manufacturer",
    "model",
    "sw_version",
    "hw_version",
    "serial_number",
    "configuration_url",
}


def _load_module(module_name: str, module_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module spec for {module_name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class UnifiedInteropContractTests(unittest.TestCase):
    """Validate dependency-free plugin interfaces and profile schema."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.icons = _load_module("icons_unified", ICONS_PATH)
        cls.availability = _load_module(
            "sensor_availability_unified", AVAILABILITY_PATH
        )
        cls.device_info = _load_module("device_info_unified", DEVICE_INFO_PATH)
        cls.profiles = _load_module("capability_profile_unified", PROFILES_PATH)

    def test_modules_import_outside_home_assistant(self) -> None:
        """Contract modules must be import-safe without HA runtime."""
        self.assertTrue(hasattr(self.icons, "resolve_sensor_icon"))
        self.assertTrue(hasattr(self.availability, "entity_enabled_default"))
        self.assertTrue(hasattr(self.device_info, "resolve_device_info"))
        self.assertTrue(hasattr(self.profiles, "CAPABILITY_PROFILES"))

    def test_contract_version_is_2_x(self) -> None:
        """Capability profile source should expose contract version."""
        self.assertRegex(self.profiles.CONTRACT_VERSION, r"^2\.\d+\.\d+$")

    def test_interface_functions_never_raise(self) -> None:
        """Interface functions should tolerate malformed inputs safely."""
        icon = self.icons.resolve_sensor_icon(object())
        self.assertTrue(icon.startswith("mdi:"))

        binary_icon = self.icons.resolve_binary_sensor_icon(None)
        self.assertTrue(binary_icon.startswith("mdi:"))

        enabled = self.availability.entity_enabled_default(None)
        self.assertIsInstance(enabled, bool)

        info = self.device_info.resolve_device_info({"firmware": object()}, "ups_snmp")
        self.assertEqual(info, {})

    def test_device_info_payload_is_canonical_and_non_empty(self) -> None:
        """Device info output must use only canonical keys with non-empty values."""
        sample = {
            "manufacturer": "APC",
            "model": "SMT1500",
            "firmware": "50.11.I",
            "serial_number": "GS123",
            "url": "https://192.168.1.10",
        }
        result = self.device_info.resolve_device_info(sample, "ups_snmp_apc_mib")
        self.assertTrue(set(result).issubset(ALLOWED_DEVICE_INFO_KEYS))
        for value in result.values():
            self.assertIsInstance(value, str)
            self.assertNotEqual(value.strip(), "")

    def test_entity_enabled_default_is_deterministic_for_all_metrics(self) -> None:
        """Availability defaults must be deterministic booleans per metric key."""
        for profile in self.profiles.CAPABILITY_PROFILES.values():
            for metric_key in profile["oids"]:
                first = self.availability.entity_enabled_default(metric_key)
                second = self.availability.entity_enabled_default(metric_key)
                self.assertIs(first, second)
                self.assertIsInstance(first, bool)

    def test_profile_schema_constraints(self) -> None:
        """Capability profiles must satisfy v2 key and poll-group constraints."""
        validation_errors = self.profiles.validate_capability_profiles()
        self.assertEqual(validation_errors, [])

        for profile_name, profile in self.profiles.CAPABILITY_PROFILES.items():
            keys = list(profile["oids"].keys())
            self.assertEqual(len(keys), len(set(keys)), profile_name)

            poll_groups = profile.get("poll_groups", {})
            for metric_key, metric_spec in profile["oids"].items():
                group = metric_spec.get("poll_group", self.profiles.DEFAULT_POLL_GROUP)
                self.assertIn(group, poll_groups, f"{profile_name}.{metric_key}")

            for block in profile.get("snmp_blocks", []):
                block_group = block.get("poll_group", self.profiles.DEFAULT_POLL_GROUP)
                self.assertIn(
                    block_group, poll_groups, f"{profile_name}.{block['name']}"
                )
                for metric in block.get("metrics", []):
                    self.assertIn(metric, profile["oids"], f"{profile_name}.{metric}")

    def test_hybrid_collision_rule_vacuously_true(self) -> None:
        """No hybrid profile in this SNMP-only project means no cross-collision risk."""
        for profile in self.profiles.CAPABILITY_PROFILES.values():
            self.assertNotEqual(profile.get("protocol"), "hybrid")


if __name__ == "__main__":
    unittest.main()
