"""Acceptance tests for device_info_unified contract."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "ups_snmp_ha"
    / "device_info_unified.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("device_info_unified", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load device_info_unified module spec")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeviceInfoUnifiedTests(unittest.TestCase):
    """Validate bridge contract behavior."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def test_import_and_contract_version(self) -> None:
        """Import should succeed outside Home Assistant and export version."""
        self.assertEqual(self.module.CONTRACT_VERSION, "1.0")

    def test_apc_sample_payload_maps_to_canonical(self) -> None:
        """APC-like payload should map to canonical keys."""
        values = {
            "manufacturer": "APC ",
            "model": " SMT1500 ",
            "firmware": "50.11.I",
            "serial_number": " GS123456 ",
            "url": "https://192.168.1.10",
        }
        result = self.module.resolve_device_info(values, "ups_snmp_apc_mib")
        self.assertEqual(
            result,
            {
                "manufacturer": "APC",
                "model": "SMT1500",
                "sw_version": "50.11.I",
                "serial_number": "GS123456",
                "configuration_url": "https://192.168.1.10",
            },
        )

    def test_ups_mib_sample_payload_maps_subset(self) -> None:
        """UPS-MIB payload should return canonical subset only."""
        values = {
            "manufacturer": "Mecer",
            "model": "ME-2000-GRU",
            "firmware": "1.0.7",
        }
        result = self.module.resolve_device_info(values, "ups_snmp_ups_mib")
        self.assertEqual(
            result,
            {
                "manufacturer": "Mecer",
                "model": "ME-2000-GRU",
                "sw_version": "1.0.7",
            },
        )

    def test_empty_or_unknown_values_omitted(self) -> None:
        """Unknown/blank values should not be returned."""
        values = {
            "manufacturer": "unknown",
            "model": "",
            "firmware": "  ",
            "serial_number": None,
            "configuration_url": "not-a-url",
        }
        result = self.module.resolve_device_info(values, "ups_snmp")
        self.assertEqual(result, {})

    def test_keys_are_subset_of_canonical(self) -> None:
        """Returned keys must be canonical only."""
        values = {
            "manufacturer": "Vendor",
            "model": "Model",
            "firmware": "1.2.3",
            "serial_number": "SN-1",
        }
        result = self.module.resolve_device_info(values, "ups_mib")
        allowed = {
            "manufacturer",
            "model",
            "sw_version",
            "hw_version",
            "serial_number",
            "configuration_url",
        }
        self.assertTrue(set(result.keys()).issubset(allowed))

    def test_no_blank_values_returned(self) -> None:
        """Returned values should be non-empty strings."""
        values = {
            "manufacturer": " APC ",
            "model": "UPS",
            "firmware": "2.0",
            "serial_number": "123",
        }
        result = self.module.resolve_device_info(values, "apc_mib")
        for key, value in result.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(value, str)
            self.assertNotEqual(value.strip(), "")

    def test_malformed_input_never_raises(self) -> None:
        """Malformed inputs should return empty dict rather than raising."""
        resolve_device_info = self.module.resolve_device_info
        self.assertEqual(resolve_device_info({}, "unsupported_source"), {})
        self.assertEqual(resolve_device_info([], "ups_snmp"), {})
        self.assertEqual(resolve_device_info(None, "ups_snmp"), {})
        self.assertEqual(resolve_device_info({"firmware": object()}, "ups_snmp"), {})


if __name__ == "__main__":
    unittest.main()
