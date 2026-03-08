# Geofences

All configured geofences for the vehicle.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/geelyTCAccess/tcservices/vehicle/geofence/all/{vin}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| `vin` | Path | Yes | Vehicle VIN |

### Headers

Standard [signed headers](../common-patterns.md#required-headers) with `authorization` token.

> **Note:** This endpoint uses the `geelyTCAccess` path prefix, indicating it routes through the Geely telematics platform.

---

## Response

The response format varies — may return a **list** directly or a **dict** with `geofences` key.

### Variant 1 — Direct list

```json
{
  "code": 1000,
  "data": [
    {
      "geofenceId": "1",
      "name": "Home",
      "centerLatitude": "48.1234",
      "centerLongitude": "11.5678",
      "radius": "500",
      "enabled": true
    }
  ]
}
```

### Variant 2 — Dict with list

```json
{
  "code": 1000,
  "data": {
    "geofences": [
      {
        "geofenceId": "1",
        "name": "Home",
        "centerLatitude": "48.1234",
        "centerLongitude": "11.5678",
        "radius": "500",
        "enabled": true
      }
    ]
  }
}
```

### Geofence Entry Fields

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `geofenceId` | string | — | Unique geofence identifier |
| `name` | string | — | User-defined geofence name |
| `centerLatitude` | string → float | degrees | Center latitude |
| `centerLongitude` | string → float | degrees | Center longitude |
| `radius` | string → int | meters | Geofence radius |
| `enabled` | bool | — | Whether geofence is active |

---

## Data Model

Returns: [`GeofenceInfo`](../models.md#geofenceinfo)

| Model Field | Source |
|-------------|--------|
| `count` | `len(geofence_list)` |
| `geofences` | Raw geofence list |

---

## Related Entities

| Entity | Platform | Device Class |
|--------|----------|-------------|
| `geofence_count` | sensor | — |

---

## Notes

- The API response format inconsistency (list vs dict) is handled by an `isinstance(data, list)` check in the parser
- Individual geofence details are stored in the raw list but not exposed as separate entities

---

## Related

- [VTM Settings](vtm-settings.md) — Geofence alerts configuration
- Source: [`api.py → async_get_geofences()`](../../custom_components/hello_smart/api.py)
