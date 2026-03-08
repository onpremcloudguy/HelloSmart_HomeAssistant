# Vehicle Running State

Condensed real-time vehicle state including power mode and speed.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/remote-control/vehicle/status/state/{vin}
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
    "engineStatus": "engine_off",
    "powerMode": "0",
    "speed": "0.0",
    "usageMode": "1",
    "carMode": "0"
  }
}
```

### Response Fields

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `engineStatus` | string | — | Engine status text (e.g., `"engine_off"`) |
| `powerMode` | string → enum | — | Ignition power mode (see mapping) |
| `speed` | string → float | km/h | Current vehicle speed |
| `usageMode` | string | — | Usage mode indicator |
| `carMode` | string | — | Car mode indicator |

### PowerMode Mapping

| Value | PowerMode Enum | Description |
|-------|---------------|-------------|
| `"0"` | `off` | Vehicle off |
| `"1"` | `accessory` | Accessory mode |
| `"2"` | `on` | Ignition on / ready to drive |
| `"3"` | `cranking` | Starting up |

---

## Data Model

Returns: [`VehicleRunningState`](../models.md#vehiclerunningstate)

| Model Field | Source |
|-------------|--------|
| `power_mode` | `powerMode` mapped to `PowerMode` enum |
| `speed` | `speed` parsed as float |

---

## Related Entities

| Entity | Platform | Device Class | Unit |
|--------|----------|-------------|------|
| `power_mode` | sensor | enum | — |
| `speed` | sensor | speed | km/h |

---

## Notes

- Provides a lightweight alternative to [Full Vehicle Status](vehicle-status.md) for real-time state
- `power_mode` also appears in the full vehicle status response; this endpoint provides a more current reading
- Speed is reported as `0.0` when the vehicle is stationary

---

## Related

- [Full Vehicle Status](vehicle-status.md) — Also includes power mode
- Source: [`api.py → async_get_vehicle_state()`](../../custom_components/hello_smart/api.py)
