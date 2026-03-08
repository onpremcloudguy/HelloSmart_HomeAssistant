# Charging Reservation

Scheduled charging configuration — start/end time and target SOC.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/remote-control/charging/reservation/{vin}
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
    "reservationStatus": "active",
    "startTime": "22:00",
    "endTime": "06:00",
    "targetSoc": "80"
  }
}
```

### Response Fields

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `reservationStatus` | string → bool | — | `"active"` = schedule enabled |
| `startTime` | string | HH:mm | Scheduled charging start |
| `endTime` | string | HH:mm | Scheduled charging end |
| `targetSoc` | string → int | % | Target state of charge |

---

## Data Model

Returns: [`ChargingReservation`](../models.md#chargingreservation)

| Model Field | Source |
|-------------|--------|
| `active` | `reservationStatus == "active"` |
| `start_time` | `startTime` |
| `end_time` | `endTime` |
| `target_soc` | `int(targetSoc)` |

---

## Related Entities

| Entity | Platform | Device Class |
|--------|----------|-------------|
| `charging_schedule_status` | sensor | enum |
| `charging_schedule_start` | sensor | — |
| `charging_schedule_end` | sensor | — |
| `charging_target_soc` | sensor | battery |

---

## Related

- [SOC / Charging Detail](soc.md) — Real-time charging data
- [Full Vehicle Status](vehicle-status.md) — Battery level, charger connection
- Source: [`api.py → async_get_charging_reservation()`](../../custom_components/hello_smart/api.py)
