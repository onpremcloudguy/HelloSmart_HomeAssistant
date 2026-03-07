# Quickstart: Hello-Smart Foundation

**Branch**: `001-hello-smart-foundation` | **Date**: 2026-03-07

## Prerequisites

- Home Assistant Core 2025.x+ (Python 3.13+)
- A Smart / Hello Smart account with at least one vehicle
- Network access to `*.smart.com` and `*.ecloudeu.com` (HTTPS port 443)

## Installation

1. Copy `custom_components/hello_smart/` into your HA `config/custom_components/` directory.
2. Restart Home Assistant.

## Setup

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **"Hello Smart"**.
3. Enter your Smart account email and password.
4. Select your region:
   - **EU** — for European accounts (auth.smart.com)
   - **INTL** — for international accounts (Australia, Singapore, Israel, etc.)
5. Click **Submit**. The integration authenticates and discovers your vehicles.
6. Each vehicle appears as a device with sensor and binary sensor entities.

## Entities Created Per Vehicle

| Entity | Type | Description |
|--------|------|-------------|
| Battery Level | Sensor (%) | Current state of charge |
| Range | Sensor (km) | Estimated remaining range |
| Charging Status | Sensor (enum) | Current charging state |
| Charging Voltage | Sensor (V) | Active charging voltage |
| Charging Current | Sensor (A) | Active charging current |
| Time to Full | Sensor (min) | Minutes until fully charged |
| Firmware Version | Sensor | Current installed firmware |
| Target Firmware | Sensor | Available firmware version |
| Charger Connected | Binary Sensor | Charging cable plugged in |
| Update Available | Binary Sensor | Firmware update pending |
| Driver Door | Binary Sensor | Open/closed |
| Passenger Door | Binary Sensor | Open/closed |
| Rear Left Door | Binary Sensor | Open/closed |
| Rear Right Door | Binary Sensor | Open/closed |
| Trunk | Binary Sensor | Open/closed |
| Windows | Binary Sensor(s) | Open/closed per window |
| Location | Device Tracker | GPS latitude/longitude |

## Configuration Options

After setup, go to the integration's **Configure** button:

- **Scan interval**: Polling frequency in seconds (default: 300 = 5 minutes)

## Verification

1. Navigate to **Developer Tools → States**.
2. Filter by `hello_smart`.
3. Verify entities show valid values (battery %, range, etc.).
4. Wait one polling interval and confirm values update.

## Diagnostics

1. Go to **Settings → Devices & Services → Hello Smart**.
2. Click the three-dot menu → **Download diagnostics**.
3. Verify the JSON contains vehicle data with sensitive fields redacted (tokens, passwords show as `**REDACTED**`).

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| "Authentication failed" during setup | Wrong credentials or region | Verify email/password work in the Hello Smart mobile app; confirm correct region |
| Entities show "unavailable" | API unreachable or tokens expired | Check network; integration will auto-recover on next poll |
| "Reauth required" notification | Password changed externally | Click the notification and re-enter credentials |
| No entities after setup | Account has no vehicles linked | Verify at least one vehicle is linked in the Hello Smart app |
