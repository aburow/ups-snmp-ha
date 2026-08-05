"""Regression checks for runtime sensor Home Assistant metadata."""

import ast
from pathlib import Path
import unittest


CONST_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "ups_snmp_ha"
    / "const.py"
)


class RuntimeSensorMetadataTests(unittest.TestCase):
    def test_runtime_sensors_are_duration_measurements(self) -> None:
        tree = ast.parse(CONST_PATH.read_text())
        descriptions = {
            next(
                keyword.value.value for keyword in node.keywords if keyword.arg == "key"
            ): {keyword.arg: ast.unparse(keyword.value) for keyword in node.keywords}
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and getattr(node.func, "id", None) == "UpsSnmpSensorDescription"
            and any(keyword.arg == "key" for keyword in node.keywords)
        }
        for key in ("runtime_remaining", "apc_runtime_remaining"):
            self.assertEqual(
                descriptions[key]["device_class"], "SensorDeviceClass.DURATION"
            )
            self.assertEqual(
                descriptions[key]["state_class"], "SensorStateClass.MEASUREMENT"
            )


if __name__ == "__main__":
    unittest.main()
