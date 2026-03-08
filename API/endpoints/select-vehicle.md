# Select Vehicle

Set the active vehicle for the current session. Required before most status endpoints.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
POST {base_url}/device-platform/user/session/update
```

### Headers

Standard [signed headers](../common-patterns.md#required-headers) with `authorization` token.

### Request Body

```json
{
  "vin": "{vin}",
  "sessionToken": "{api_access_token}",
  "language": ""
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `vin` | string | Yes | Vehicle VIN from [List Vehicles](list-vehicles.md) |
| `sessionToken` | string | Yes | Current API access token |
| `language` | string | No | Language code (empty string for default) |

---

## Response

```json
{
  "code": 1000,
  "data": null,
  "success": true
}
```

Returns standard envelope with `null` data on success.

---

## Notes

- Must be called before querying any vehicle-specific endpoints
- Sets a server-side session — the selected vehicle persists until changed
- The coordinator calls this once per vehicle before fetching all status endpoints
- Some endpoints (like [VTM Settings](vtm-settings.md)) don't include the VIN in the path and rely entirely on this session

---

## Related

- [List Vehicles](list-vehicles.md) — Provides the VIN to select
- Source: [`api.py → async_select_vehicle()`](../../custom_components/hello_smart/api.py)
