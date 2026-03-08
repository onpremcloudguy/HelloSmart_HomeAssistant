# VTM Settings

Vehicle Theft Monitoring (VTM) configuration — master switch, notifications, and geofence alerts.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/remote-control/getVtmSettingStatus
```

> **Note:** No `{vin}` in the path — this endpoint uses the [selected vehicle session](select-vehicle.md).

### Headers

Standard [signed headers](../common-patterns.md#required-headers) with `authorization` token.

---

## Response

```json
{
  "code": 1000,
  "data": {
    "vtmEnabled": true,
    "notificationEnabled": true,
    "geofenceAlertEnabled": true,
    "movementAlertEnabled": true
  }
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `vtmEnabled` | bool | VTM master switch |
| `notificationEnabled` | bool | Push notifications for VTM events |
| `geofenceAlertEnabled` | bool | Alert when vehicle leaves a geofence |
| `movementAlertEnabled` | bool | Alert on unexpected vehicle movement |

---

## Data Model

Returns: [`VtmSettings`](../models.md#vtmsettings)

| Model Field | Source |
|-------------|--------|
| `enabled` | `vtmEnabled` |
| `notification_enabled` | `notificationEnabled` |
| `geofence_alert_enabled` | `geofenceAlertEnabled` |

---

## Related Entities

| Entity | Platform | Device Class |
|--------|----------|-------------|
| `vtm_enabled` | binary_sensor | — |
| `vtm_notification_enabled` | binary_sensor | — |
| `vtm_geofence_alert` | binary_sensor | — |

---

## Known Issues

- Returns code `1405` ("not found resource") on vehicles without VTM feature
- Handled gracefully — entities are hidden when data is unavailable

---

## Related

- [Geofences](geofences.md) — Geofence configurations used by VTM
- [Select Vehicle](select-vehicle.md) — Must be called first (no VIN in path)
- Source: [`api.py → async_get_vtm_settings()`](../../custom_components/hello_smart/api.py)
