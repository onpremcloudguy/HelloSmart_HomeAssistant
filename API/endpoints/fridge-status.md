# Mini-Fridge Status

Smart #1 optional mini-fridge in center console.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/remote-control/getFridge/status/{vin}
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
    "fridgeStatus": "on",
    "temperature": "5",
    "mode": "cooling"
  }
}
```

### Response Fields

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `fridgeStatus` | string → bool | — | `"on"` = fridge is running |
| `temperature` | string → float | °C | Current fridge temperature |
| `mode` | string | — | `"cooling"`, `"warming"`, or `"off"` |

---

## Data Model

Returns: [`FridgeStatus`](../models.md#fridgestatus)

| Model Field | Source |
|-------------|--------|
| `active` | `fridgeStatus == "on"` |
| `temperature` | `float(temperature)` |
| `mode` | `mode` |

---

## Related Entities

| Entity | Platform | Device Class | Unit |
|--------|----------|-------------|------|
| `fridge_active` | binary_sensor | running | — |
| `fridge_temperature` | sensor | temperature | °C |
| `fridge_mode` | sensor | enum | — |

---

## Known Issues

- Returns code `1405` ("not found resource") on vehicles without fridge option
- Handled gracefully — entities are hidden when data is unavailable

---

## Related

- Source: [`api.py → async_get_fridge_status()`](../../custom_components/hello_smart/api.py)
