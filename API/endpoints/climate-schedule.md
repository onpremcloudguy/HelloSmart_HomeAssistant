# Climate Schedule

Climate pre-conditioning schedule — time, temperature, and duration.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/remote-control/schedule/{vin}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| `vin` | Path | Yes | Vehicle VIN |

### Headers

Standard [signed headers](../common-patterns.md#required-headers) with `authorization` token.

---

## Response

The response format varies — may return a **dict** with `scheduleList` or a **list** directly.

### Variant 1 — Dict with list

```json
{
  "code": 1000,
  "data": {
    "scheduleList": [
      {
        "scheduleId": "1",
        "enabled": true,
        "scheduledTime": "07:00",
        "temperature": "21.0",
        "duration": 180
      }
    ]
  }
}
```

### Variant 2 — Direct list

```json
{
  "code": 1000,
  "data": [
    {
      "scheduleId": "1",
      "enabled": true,
      "scheduledTime": "07:00",
      "temperature": "21.0",
      "duration": 180
    }
  ]
}
```

### Response Fields (per schedule entry)

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| `scheduleId` | string | — | Schedule identifier |
| `enabled` | bool | — | Whether this schedule is active |
| `scheduledTime` | string | HH:mm | Activation time |
| `temperature` | string → float | °C | Target cabin temperature |
| `duration` | int | seconds | Pre-conditioning duration |

---

## Data Model

Returns: [`ClimateSchedule`](../models.md#climateschedule) `| None`

Only the **first** schedule entry is returned. Returns `None` if the list is empty.

| Model Field | Source |
|-------------|--------|
| `enabled` | `scheduleList[0].enabled` |
| `scheduled_time` | `scheduleList[0].scheduledTime` |
| `temperature` | `float(scheduleList[0].temperature)` |
| `duration` | `scheduleList[0].duration` |

---

## Related Entities

| Entity | Platform | Device Class | Unit |
|--------|----------|-------------|------|
| `climate_schedule_status` | sensor | enum | — |
| `climate_schedule_time` | sensor | — | — |
| `climate_schedule_temp` | sensor | temperature | °C |
| `climate_schedule_duration` | sensor | duration | s |

---

## Notes

- The API response format inconsistency (list vs dict) is handled by an `isinstance(data, list)` check in the parser
- Only the first schedule is exposed as entities — multiple schedules are not yet supported

---

## Related

- [Full Vehicle Status](vehicle-status.md) — Includes `climateActive` and temperatures
- Source: [`api.py → async_get_climate_schedule()`](../../custom_components/hello_smart/api.py)
