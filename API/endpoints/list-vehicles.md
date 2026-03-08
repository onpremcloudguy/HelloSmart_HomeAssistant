# List Vehicles

Fetch all vehicles linked to the authenticated account.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/device-platform/user/vehicle/secure?needSharedCar=1&userId={userId}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| `needSharedCar` | Query | Yes | Include shared vehicles (`1` = yes) |
| `userId` | Query | Yes | Authenticated user ID from login |

### Headers

Standard [signed headers](../common-patterns.md#required-headers) with `authorization` token.

---

## Response

```json
{
  "code": 1000,
  "data": {
    "list": [
      {
        "vin": "HESCA2...",
        "modelName": "CM590 HC11 Performance 4WD RHD APAC",
        "modelYear": "2025",
        "seriesCodeVs": "HC11"
      }
    ]
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `vin` | string | Vehicle Identification Number |
| `modelName` | string | Full model name |
| `modelYear` | string | Model year |
| `seriesCodeVs` | string | Series/variant code |

---

## Data Model

Returns: `list[Vehicle]`

See [Vehicle model](../models.md#vehicle)

---

## Notes

- This is typically the first endpoint called after authentication
- Returns all vehicles including shared ones when `needSharedCar=1`
- The VIN from this response is used in all subsequent vehicle-specific endpoints

---

## Related

- [Select Vehicle](select-vehicle.md) — Must be called next to set the active vehicle
- Source: [`api.py → async_get_vehicles()`](../../custom_components/hello_smart/api.py)
