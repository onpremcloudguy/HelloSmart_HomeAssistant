# SOC / Charging Detail

Supplementary charging data — voltage, current, and estimated time to full charge.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/remote-control/vehicle/status/soc/{vin}?setting=charging
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| `vin` | Path | Yes | Vehicle VIN |
| `setting` | Query | Yes | Always `charging` |

### Headers

Standard [signed headers](../common-patterns.md#required-headers) with `authorization` token.

---

## Response

```json
{
  "code": 1000,
  "data": {
    "chargeUAct": "7.2",
    "chargeIAct": "32.0",
    "timeToFullyCharged": "180"
  }
}
```

### Response Fields

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `chargeUAct` | string → float | V | Active charging voltage |
| `chargeIAct` | string → float | A | Active charging current |
| `timeToFullyCharged` | string → int | minutes | Estimated time to fully charged |

---

## Data Model

Enriches: [`VehicleStatus`](../models.md#vehiclestatus)

| VehicleStatus Field | Source |
|---------------------|--------|
| `charge_voltage` | `chargeUAct` |
| `charge_current` | `chargeIAct` |
| `time_to_full` | `timeToFullyCharged` |

---

## Related Entities

| Entity | Platform | Device Class | Unit |
|--------|----------|-------------|------|
| `charge_voltage` | sensor | voltage | V |
| `charge_current` | sensor | current | A |
| `time_to_full` | sensor | duration | min |

---

## Notes

- Values are only meaningful when the vehicle is actively charging
- Returns `None`/empty values when not charging
- This endpoint supplements the main [Vehicle Status](vehicle-status.md) endpoint

---

## Related

- [Full Vehicle Status](vehicle-status.md) — Primary status endpoint
- [Charging Reservation](charging-reservation.md) — Scheduled charging
- Source: [`api.py → async_get_soc()`](../../custom_components/hello_smart/api.py)
