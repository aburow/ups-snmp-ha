# ups-snmp-ha

![HACS](https://img.shields.io/badge/HACS-Default-orange.svg)
![HACS Validation](https://github.com/aburow/ups-snmp-ha/actions/workflows/hacs.yaml/badge.svg)
![Hassfest](https://github.com/aburow/ups-snmp-ha/actions/workflows/hassfest.yaml/badge.svg)

Home Assistant integration for monitoring UPS devices via SNMP with a focus on RFC1628 (UPS-MIB) and a fallback to APC enterprise OIDs when RFC1628 is unavailable.

This custom component runs standalone and does not require NUT or APCUPSD.

## Features

- **SNMP-only polling** with per-device config entries
- **RFC1628 UPS-MIB first**, APC enterprise fallback when needed
- **Cross-vendor output load support**:
  - UPS-MIB `upsOutputPercentLoad` with index fallback (`...5.1` then `...5.0`)
  - APC enterprise output load fallback when UPS-MIB is unavailable
- **Fast/slow polling split**:
  - Fast (default 10s): AC power state + remaining runtime + output load
  - Slow (default 5 min): inventory + other sensors
- **Core-first entity defaults**:
  - Core UPS entities are enabled by default
  - Non-core entities are created disabled by default and can be enabled in Entity Registry
- **Enabled-only non-core polling**:
  - Core and profiling keys are always polled
  - Non-core SNMP keys are polled only when their entities are enabled
- **Missing OID suppression**:
  - Detects non-existent OIDs (`noSuchObject` / `noSuchInstance`) and skips them on future polls
  - Keeps empty/null values as non-fatal responses
- **Local communication** (no cloud dependency)
- **Event-loop safe SNMP** (pysnmp work offloaded to executor)
- **No new dependencies** beyond Home Assistant’s bundled pysnmp

## Installation

### Using HACS (Recommended)

1. Go to HACS in Home Assistant
2. Click the three-dot menu and select "Custom repositories"
3. Add repository: `https://github.com/aburow/ups-snmp-ha`
4. Select "Integration" category
5. Install "UPS SNMP"
6. Restart Home Assistant

### Manual Installation

1. Copy `custom_components/ups_snmp_ha/` to `config/custom_components/` on your Home Assistant instance
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Integrations
4. Click "Create Integration"
5. Search for "UPS SNMP"

## Configuration

Each device is configured as its own integration entry:

1. Go to **Settings → Devices & Services → Integrations**
2. Click **Create Integration**
3. Search for and select **UPS SNMP**
4. Fill in the required configuration:
   - **Host**: UPS IP or hostname
   - **SNMP Community**: SNMP community string (default: "public")
5. Optional advanced settings:
   - **Device Name**: Friendly name (default: "UPS")
   - **Fast Poll Interval**: AC power + runtime (default: 10s)
   - **Slow Poll Interval**: All other values (default: 300s)

## SNMP Requirements

- SNMP enabled on the device (UDP/161)
- Community string configured (default: `public`)

The integration attempts SNMPv2c first, then SNMPv1 if required.

## Supported Devices

Any UPS exposing RFC1628 (UPS-MIB) should work. APC devices with older cards that do not expose UPS-MIB are supported via APC enterprise OIDs for core values.

## Troubleshooting

Enable debug logging:

```yaml
logger:
  logs:
    custom_components.ups_snmp_ha: debug
    custom_components.ups_snmp_ha.coordinator: debug
    custom_components.ups_snmp_ha.snmp_helper: debug
```

Useful debug signals to look for:

- `Starting SNMP update` with device name, host, entry_id
- `Waited Xs for SNMP lock` when overlapping polls are serialized
- `SNMP update failed ... backing off` for exponential backoff on failures

Check for SNMP connectivity and community string correctness. If a device does not expose UPS-MIB, the integration will automatically fall back to APC enterprise OIDs when available.

For RFC1628 debugging, collect a full UPS-MIB walk:

```bash
snmpwalk -v2c -c <community> <ups_host_or_ip> 1.3.6.1.2.1.33
```

Not all SNMP implementations are created equal. Even when a device claims adherence to a given RFC (such as RFC 1628), differences in interpretation, partial implementations, and resource constraints can result in incomplete or non-conformant MIBs and unreliable GETBULK behavior, despite advertising SNMPv2c or later. For this reason, the integration uses defensive SNMP querying rather than relying solely on declared RFC compliance; when reporting issues, please include the device manufacturer, model, firmware version, SNMP version, affected OIDs or tables, and what query methods (if any) work reliably.

## Architecture

- Here’s a concise block diagram of the integration and responsibilities:

```text
+------------------------------------------------------+
| Home Assistant (core runtime + scheduler)            |
+------------------------------------------------------+
                         |
                         v
+------------------------------------------------------+
| UpsSnmpCoordinator                                    |
| - schedules fast/slow polls                          |
| - detects MIB + SNMP version                         |
| - merges SNMP data + derived states                  |
| - suppresses missing OIDs after detection            |
| - raises UpdateFailed on no data                     |
+------------------------------------------------------+
                |                            |
                | entity updates             | polling
                v                            v
+---------------------------------------------+   +------------------------------------------------------+
| Sensor / Binary Sensor modules             |   | snmp_helper                                          |
| - map coordinator data to HA entities      |   | - sends SNMP queries                                 |
| - expose values/states to HA               |   | - runs in executor threads                           |
+---------------------------------------------+   | - distinguishes missing OIDs from empty/null values |
                                                  +------------------------------------------------------+
                                                      ^                           ^
                                                      | Fast poll (10s default)  | Slow poll (300s default)
                                                      | - output source/state    | - inventory + other stats
                                                      | - runtime remaining      |
                                                      | - output load            |
                                                      +---------------------------+
                                                                   |
                                                                   | SNMP GETs (executor)
                                                                   v
                                                  +------------------------------------------------------+
                                                  | UPS device (SNMP agent)                              |
                                                  | - exposes UPS-MIB and/or APC enterprise OIDs         |
                                                  +------------------------------------------------------+
```

Component responsibilities (short list):

- UpsSnmpCoordinator: polling cadence, MIB detection, data normalization, derived states, error handling.
- snmp_helper: SNMP transport, per-OID GETs, missing-OID detection, empty/null handling, executor offload.
- sensor.py / binary_sensor.py: entity definitions and presentation in HA.
- icons_unified.py: shared standalone icon mapping resolver used as the canonical source across UPS projects.
- UPS SNMP agent: provides OID values via UPS-MIB/APC enterprise OIDs.

## Developer Linting

This repository uses `uv` + `pre-commit` for local linting.

```bash
# Prepare lint environment and tools
make lint-bootstrap

# Run standard hooks (quick pass)
make lint-fast

# Run all hooks including manual-stage checks
make lint

# Apply auto-fixable Ruff changes
make lint-fix

# Run CodeQL security scan (requires codeql installed)
make lint-security
```

To run hooks automatically on every commit:

```bash
uv sync --group lint
uv run pre-commit install
```

Manual-stage hooks include `yamllint`, `shellcheck`, `shfmt`, `sqlfluff`, and `semgrep`.
