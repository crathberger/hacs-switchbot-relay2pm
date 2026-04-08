# SwitchBot Relay Switch 2PM — Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A custom Home Assistant integration for the **SwitchBot Relay Switch 2PM** configured in **roller blind / shutter mode**.

The official SwitchBot integration in Home Assistant only exposes the two relay channels as plain switches — it does not support the roller blind mode configured in the SwitchBot app. This integration solves that by using the SwitchBot Cloud API v1.1 to expose a proper **Cover entity** with open, close, stop, and set position support.

## Features

- **Cover entity** (device class: shutter) with full control:
  - Open / Close / Stop
  - Set position (0–100%)
- **Power monitoring sensors** per channel (Watt, Volt, Ampere)
- Automatic device discovery — just enter your API credentials and pick your device
- Polling every 30 seconds
- English and German UI translations

## Requirements

- SwitchBot Relay Switch 2PM configured as a roller blind in the SwitchBot app
- SwitchBot API Token and Secret Key (SwitchBot app → Profile → Developer Options, requires app v6.14+)
- Home Assistant 2024.1.0 or newer

## Installation via HACS

1. Open HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/crathberger/hacs-switchbot-relay2pm` as an **Integration**
3. Search for "SwitchBot Relay Switch 2PM" and install
4. Restart Home Assistant

## Manual Installation

Copy the `custom_components/switchbot_relay2pm` folder into your HA `config/custom_components/` directory and restart Home Assistant.

## Configuration

1. Go to **Settings → Integrations → + Add Integration**
2. Search for **SwitchBot Relay Switch 2PM**
3. Enter your API Token and Secret Key
4. Select your device (auto-discovered from your account)

## API Credentials

Open the SwitchBot app → tap your profile picture → **Developer Options** → copy Token and Secret Key.

> **Note:** The SwitchBot API allows 10,000 requests per day. With 30-second polling this integration uses ~2,880 requests/day, well within the limit.

## Limitations

- Requires internet connection (SwitchBot Cloud API)
- Energy metering history not tracked (daily consumption resets in SwitchBot cloud)
- Stop command sends `setPosition` to current position — motor may move slightly before stopping

## Supported Devices

| Device | Mode |
|--------|------|
| SwitchBot Relay Switch 2PM | Roller blind / shutter |

## License

MIT
