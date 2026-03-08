# Telematics Status

Connectivity status and telematics unit metadata.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/remote-control/vehicle/telematics/{vin}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| `vin` | Path | Yes | Vehicle VIN |

### Headers

Standard [signed headers](../common-patterns.md#required-headers) with `authorization` token.

---

## Response

```json
{
  "code": 1000,
  "data": {
    "swVersion": "v1.2.3",
    "hwVersion": "HW2.0",
    "imei": "123456789012345",
    "connectivityStatus": "connected",
    "powerMode": "0",
    "backupBattery": {
      "voltage": "12.4",
      "stateOfCharge": "95"
    }
  }
}
```

### Response Fields

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `swVersion` | string | — | Telematics software version |
| `hwVersion` | string | — | Telematics hardware version |
| `imei` | string | — | Telematics unit IMEI |
| `connectivityStatus` | string → bool | — | `"connected"` = online |
| `powerMode` | string → enum | — | Telematics unit power mode |

### Backup Battery

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `voltage` | string → float | V | Backup battery voltage |
| `stateOfCharge` | string → float | % | Backup battery charge level |

---

## Data Model

Returns: [`TelematicsStatus`](../models.md#telematicsstatus)

| Model Field | Source |
|-------------|--------|
| `connected` | `connectivityStatus == "connected"` |
| `sw_version` | `swVersion` |
| `hw_version` | `hwVersion` |
| `imei` | `imei` |
| `power_mode` | `powerMode` mapped to `PowerMode` enum |
| `backup_battery_voltage` | `backupBattery.voltage` |
| `backup_battery_level` | `backupBattery.stateOfCharge` |

---

## Related Entities

| Entity | Platform | Device Class | Unit |
|--------|----------|-------------|------|
| `telematics_connected` | binary_sensor | connectivity | — |
| `backup_battery_voltage` | sensor | voltage | V |
| `backup_battery_level` | sensor | battery | % |

---

## Known Issues

- Returns HTTP error on some INTL regions — handled gracefully with `except Exception`
- `imei` is in the `SENSITIVE_FIELDS` list and redacted in diagnostics exports

---

## Related

- [Full Vehicle Status](vehicle-status.md) — Includes some overlapping power mode data
- Source: [`api.py → async_get_telematics()`](../../custom_components/hello_smart/api.py)
