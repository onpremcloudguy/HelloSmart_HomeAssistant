# Total Distance

Cumulative odometer reading from the telematics cloud.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/geelyTCAccess/tcservices/vehicle/status/getTotalDistanceByLabel/{vin}
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
    "totalDistance": "12345.6",
    "label": "total",
    "updateTime": "1706028240000"
  }
}
```

### Response Fields

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `totalDistance` | string → float | km | Cumulative distance driven |
| `label` | string | — | Distance category (`"total"`) |
| `updateTime` | string → datetime | — | Last update timestamp (epoch ms) |

---

## Data Model

Returns: `float | None` — total distance in km

---

## Related Entities

| Entity | Platform | Device Class | Unit |
|--------|----------|-------------|------|
| `total_distance` | sensor | distance | km |

---

## Notes

- This is an alternative to the `odometer` value from [Vehicle Status](vehicle-status.md)
- May differ slightly from the vehicle status odometer as it's sourced from the telematics cloud rather than the vehicle CAN bus
- Returns code `8153` ("Connection interruption") on some INTL regions

---

## Related

- [Full Vehicle Status](vehicle-status.md) — Also includes `odometer`
- [Trip Journal](trip-journal.md) — Per-trip distances
- Source: [`api.py → async_get_total_distance()`](../../custom_components/hello_smart/api.py)
