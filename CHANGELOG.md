# Changelog

All notable changes to the UPS SNMP integration will be documented in this file.

## [1.1.1-dev5] - 2026-04-12

- Add `custom_components/ups_snmp_ha/device_info_unified.py` for ups-docker-ha bridge compatibility
- Export `CONTRACT_VERSION = "1.0"` and `resolve_device_info(values, source)` with canonical device metadata output
- Ensure device info resolver is dependency-free, HA-import free, deterministic, and safe-fallback (`{}`) for unsupported/malformed inputs
- Add acceptance tests for bridge contract behavior in `tests/test_device_info_unified.py`

## [1.1.1-dev4] - 2026-04-12

- Harden `sensor_availability_unified.entity_enabled_default()` to never raise and return `True` on exception, matching ups-docker-ha compatibility contract requirements
- Confirm additive contract compliance for external module loading from ups-docker-ha:
  - `icons_unified.py` exports required icon resolvers with `mdi:*` defaults
  - `sensor_availability_unified.py` exports `entity_enabled_default(local_entity_key: str) -> bool`

## [1.1.1-dev3] - 2026-04-11

- Add dependency-free unified availability template for canonical core metric membership and local key adapters
- Default-enable only core entities; non-core entities are Entity Registry opt-in by default
- Make SNMP polling protocol-aware and availability-aware:
  - poll protocol-valid core keys by default (APC and non-APC aware)
  - poll non-core keys only when their entities are enabled
  - keep required profiling and derived-state dependency keys always polled
- Keep protocol detection, device profiling, and missing-OID suppression behavior unchanged

## [1.1.1-dev2] - 2026-04-11

- Expand unified sensor icon mapping with explicit state/condition keys for `buzzer_muted`, power/failure states, overload, bypass, and output conditions
- Prioritize these state/condition keys before generic `load`/`status` matches to improve deterministic icon selection for alarm-like metrics

## [1.1.1-dev1] - 2026-04-11

- Replace in-module icon pattern tables with the shared standalone [icons_unified.py] icon resolver
- Add `custom_components/ups_snmp_ha/icons_unified.py` as the canonical cross-project icon mapping source
- Keep deterministic icon assignment in entity setup while delegating all mapping logic to unified resolver functions

## [1.1.0] - 2026-04-11

- Add deterministic `mdi:` icon resolution for sensors and binary sensors to avoid frontend fallback icon mismatches
- Add semantic icon mapping helpers keyed by entity key/data key patterns, including future dynamic key families
- Add state-aware binary sensor icons for on/off representation
- Add local `uv` + `pre-commit` lint framework with manual tasks (`make lint`, `make lint-fix`, `make lint-security`)
- Add manual security/style hooks for semgrep, sqlfluff, shellcheck, shfmt, and CodeQL
- Add project-local CodeQL runner isolation to avoid cross-repo concurrency collisions
- Refresh developer documentation for lint bootstrap and execution flow

## [1.0.3] - 2026-02-18

- Add robust handling for missing OIDs by distinguishing `noSuchObject` / `noSuchInstance` / `endOfMibView` from empty values
- Cache unsupported OIDs per device and skip them on future polls
- Add UPS-MIB output load fallback from `.1.3.6.1.2.1.33.1.4.4.1.5.1` to `.1.3.6.1.2.1.33.1.4.4.1.5.0` for devices with alternate indexing
- Add multi-OID key resolution support so metrics can probe OIDs in priority order
- Update documentation and debugging guidance for fast/slow polling behavior and RFC1628 walk troubleshooting

## [1.0.3-dev2] - 2026-02-18

- Add UPS-MIB output load fallback for devices exposing `upsOutputPercentLoad` at `.5.0` instead of `.5.1`
- Add multi-OID key resolution so a metric can try OIDs in priority order

## [1.0.3-dev1] - 2026-02-18

- Detect non-existent OIDs (`noSuchObject` / `noSuchInstance` / `endOfMibView`) separately from empty/null values
- Cache and skip unsupported OIDs on future polls for each device

## [1.0.2] - 2026-02-18

- Move `output_load` to fast polling (default 10s), matching runtime cadence

## [1.0.1] - 2026-02-18

- Add `output_load` sensor entity (`%`) for Home Assistant
- Add RFC1628 UPS-MIB output load OID support alongside existing APC enterprise support

## [1.0.0] - 2026-02-08

- Mark the integration as stable 1.0.0 with no functional changes since 0.4.7

## [0.4.7] - 2026-01-29

- Offload pysnmp queries to executor threads to avoid blocking the HA event loop
- Serialize SNMP polling per host and add exponential backoff for repeated failures
- Add clearer debug logging for polling, lock waits, and backoff

## [0.4.6] - 2026-01-29

- Remove pysnmp requirement to use Home Assistant’s bundled version

## [0.4.5] - 2026-01-29

- Show human-readable battery status for UPS-MIB and APC devices

## [0.4.4] - 2026-01-29

- Poll battery charge and input voltage on the fast interval for UPS-MIB and APC devices

## [0.4.3] - 2026-01-28

- Poll seconds on battery on the fast interval

## [0.4.2] - 2026-01-28

- Reorder sensors so fast-poll values appear first, then slow-poll values alphabetically

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
