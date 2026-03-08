# Fragrance System

In-cabin fragrance diffuser status, level, and type.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/remote-control/vehicle/fragrance/{vin}
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
    "fragranceActive": false,
    "fragranceLevel": "high",
    "fragranceType": "1"
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `fragranceActive` | bool | Whether fragrance is currently diffusing |
| `fragranceLevel` | string | Cartridge level: `"high"`, `"medium"`, `"low"`, or `"empty"` |
| `fragranceType` | string | Fragrance cartridge type identifier |

---

## Data Model

Returns: [`FragranceDetails`](../models.md#fragrancedetails)

| Model Field | Source |
|-------------|--------|
| `active` | `fragranceActive` |
| `level` | `fragranceLevel` |
| `fragrance_type` | `fragranceType` |

---

## Related Entities

| Entity | Platform | Device Class |
|--------|----------|-------------|
| `fragrance_active` | binary_sensor | — |
| `fragrance_level` | sensor | — |

---

## Notes

- Fragrance active state is also available in the main [Vehicle Status](vehicle-status.md) response under `climateStatus.fragActive`
- The fragrance-specific endpoint provides additional detail (level, type) not in the main status

---

## Related

- [Full Vehicle Status](vehicle-status.md) — Also reports `fragActive`
- Source: [`api.py → async_get_fragrance()`](../../custom_components/hello_smart/api.py)
