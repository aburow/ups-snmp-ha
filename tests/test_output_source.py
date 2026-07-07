# SPDX-License-Identifier: AGPL-3.0-or-later

"""Regression tests for SNMP output-source state derivation."""

import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "ups_snmp_ha"
    / "output_source.py"
)


def _load_module():
    spec = importlib.util.spec_from_file_location("output_source", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OutputSourceTests(unittest.TestCase):
    """Verify RFC1628 and APC output-source semantics."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()

    def test_ups_mib_all_rfc1628_values(self) -> None:
        """Treat AVR boost and buck as online AC operation."""
        expected = {
            1: ("other", None),
            2: ("none", False),
            3: ("normal", True),
            4: ("bypass", True),
            5: ("battery", False),
            6: ("booster", True),
            7: ("reducer", True),
        }

        for value, (source, ac_power) in expected.items():
            with self.subTest(value=value):
                result = self.module.derive_output_states("ups_mib", value)
                self.assertEqual(result["output_source"], source)
                self.assertEqual(result["ac_power"], ac_power)

    def test_rfc_and_apc_status_names_remain_distinct(self) -> None:
        """Do not replace RFC1628 values with APC PowerNet terminology."""
        rfc_state = self.module.derive_output_states("ups_mib", 7)
        apc_state = self.module.derive_output_states("apc_mib", 12)

        self.assertEqual(rfc_state["output_source"], "reducer")
        self.assertEqual(apc_state["output_source"], "smart_trim")

    def test_ups_mib_battery_and_bypass_states(self) -> None:
        """Preserve battery and bypass state derivation."""
        self.assertTrue(
            self.module.derive_output_states("ups_mib", 5)["on_battery"]
        )
        self.assertTrue(
            self.module.derive_output_states("ups_mib", 4)["on_bypass"]
        )

    def test_apc_mib_values(self) -> None:
        """Map common APC enterprise output-source semantics."""
        expected = {
            1: ("other", None),
            2: ("online", True),
            3: ("battery", False),
            4: ("smart_boost", True),
            6: ("software_bypass", True),
            9: ("switched_bypass", True),
            10: ("hardware_failure_bypass", True),
            12: ("smart_trim", True),
            13: ("eco_mode", True),
            16: ("emergency_static_bypass", True),
            20: ("e_conversion", True),
            23: ("active_load", True),
        }

        for value, (source, ac_power) in expected.items():
            with self.subTest(value=value):
                result = self.module.derive_output_states("apc_mib", value)
                self.assertEqual(result["output_source"], source)
                self.assertEqual(result["ac_power"], ac_power)

    def test_all_apc_output_status_values_have_names(self) -> None:
        """Expose every PowerNet output status without collapsing detail."""
        for value in range(1, 29):
            with self.subTest(value=value):
                result = self.module.derive_output_states("apc_mib", value)
                self.assertNotEqual(result["output_source"], "unknown")

    def test_apc_bypass_variants(self) -> None:
        """Recognize every APC bypass variant as bypass operation."""
        for value in (6, 9, 10, 16, 17):
            with self.subTest(value=value):
                result = self.module.derive_output_states("apc_mib", value)
                self.assertTrue(result["on_bypass"])

    def test_invalid_value_is_unknown(self) -> None:
        """Do not report an invalid or unrecognized value as AC off."""
        for value in (None, "invalid", 99):
            with self.subTest(value=value):
                result = self.module.derive_output_states("ups_mib", value)
                self.assertEqual(result["output_source"], "unknown")
                self.assertIsNone(result["ac_power"])
