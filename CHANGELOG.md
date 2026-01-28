# Changelog

All notable changes to the UPS SNMP integration will be documented in this file.

## [0.4.1] - 2026-01-28

- Fix handling of missing SNMP values so protocol detection can fall back cleanly

## [0.4.0] - 2026-01-28

### Added
- SNMP-only polling with RFC1628 (UPS-MIB) primary support and APC enterprise fallback
- Fast/slow polling split for runtime and AC power vs. other metrics
- SNMPv2c to SNMPv1 autodetect for older management cards

### Changed
- Integration branding updated for ups-snmp-ha

---

## [0.3.4] - 2026-01-26

### Added
- UPS SNMP branded icons for the integration
- Rack PDU SNMP OIDs and phase sensor block reads for improved coverage

### Changed
- Integration icon updated to `mdi:uninterruptible-power-supply`

### Fixed
- SNMP async API usage updated for pysnmp v3arch compatibility (PySnmp 7.1.22)
- Removed invalid manifest icon reference

## [0.1.0] - 2026-01-25

### Added
- Initial release of UPS SNMP integration
- SNMP protocol support
- Configuration UI for easy setup
- Support for multiple UPS devices
- Battery status, load, voltage, and temperature monitoring
- Power source and runtime monitoring
- Firmware and device information via SNMP

### Features
- Real-time UPS status monitoring
- Input/output voltage and current sensors
- Battery charge percentage and runtime estimation
- Device model, serial number, and firmware version (via SNMP)
- Graceful fallback when specific OIDs are unavailable

### Fixed
- Resolved SNMP dependency conflict with Home Assistant core
- Improved error handling for connection timeouts

---

For detailed information about each release, visit the [releases page](https://github.com/aburow/ups-snmp-ha/releases).
