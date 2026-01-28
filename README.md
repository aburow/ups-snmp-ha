# ups-snmp-ha

![HACS](https://img.shields.io/badge/HACS-Default-orange.svg)
![HACS Validation](https://github.com/aburow/ups-snmp-ha/actions/workflows/hacs.yml/badge.svg)
![Hassfest](https://github.com/aburow/ups-snmp-ha/actions/workflows/hassfest.yml/badge.svg)

Home Assistant integration for monitoring UPS devices via SNMP with a focus on RFC1628 (UPS-MIB) and a fallback to APC enterprise OIDs when RFC1628 is unavailable.

This custom component runs standalone and does not require NUT or APCUPSD.

## Features

- **SNMP-only polling** with per-device config entries
- **RFC1628 UPS-MIB first**, APC enterprise fallback when needed
- **Fast/slow polling split**:
  - Fast (default 10s): AC power state + remaining runtime
  - Slow (default 5 min): inventory + other sensors
- **Local communication** (no cloud dependency)

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
```

Check for SNMP connectivity and community string correctness. If a device does not expose UPS-MIB, the integration will automatically fall back to APC enterprise OIDs when available.
