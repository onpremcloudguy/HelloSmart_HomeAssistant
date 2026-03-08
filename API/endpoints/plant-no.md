# Factory Plant Number

Vehicle factory/plant identification code.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/geelyTCAccess/tcservices/customer/vehicle/plantNo/{vin}
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
    "plantNo": "..."
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `plantNo` | string | Factory/plant identification number |

---

## Data Model

Returns: `str` — factory plant number

---

## Usage

The plant number is used as metadata in the Home Assistant `DeviceInfo`:

```python
DeviceInfo(
    manufacturer=f"Smart ({plant_no})",  # when available
)
```

---

## Notes

- This endpoint is called once during coordinator setup
- The value is used for device info enrichment, not exposed as a separate entity
- Falls back gracefully if unavailable

---

## Related

- [List Vehicles](list-vehicles.md) — Vehicle identification
- Source: [`api.py → async_get_plant_no()`](../../custom_components/hello_smart/api.py)
