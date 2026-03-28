# Contract: Capability API Response Schema

**Type**: External API (inbound data)
**Endpoint**: `GET /geelyTCAccess/tcservices/capability/{vin}`
**Owner**: Smart/Geely cloud platform (external, read-only)

## Expected Response Structure

Based on APK `TscVehicleCapability.java` and `Capability.java` (authoritative model).

> **NOTE**: This schema is derived from APK decompilation. A live API response
> capture is required during implementation to verify field names and nesting.

```json
{
  "code": 1000,
  "data": {
    "list": [
      {
        "functionId": "remote_control_lock",
        "valueEnable": true,
        "functionCategory": "remote_control",
        "name": "Remote Lock",
        "showType": "switch",
        "tips": "",
        "valueEnum": "",
        "valueRange": "",
        "paramsJson": [],
        "configCode": "",
        "platform": "tsp",
        "priority": 1,
        "vin": "WMEXXXXXXXXXXXXXXX",
        "modelCode": "HX11",
        "id": 1
      },
      {
        "functionId": "remote_air_condition_switch",
        "valueEnable": true,
        "functionCategory": "remote_control",
        "name": "Remote AC",
        "showType": "switch",
        "tips": "",
        "valueEnum": "",
        "valueRange": "16|28",
        "paramsJson": [],
        "configCode": "",
        "platform": "tsp",
        "priority": 2,
        "vin": "WMEXXXXXXXXXXXXXXX",
        "modelCode": "HX11",
        "id": 2
      }
    ],
    "serviceResult": {
      "code": "200",
      "message": "success"
    }
  },
  "success": true,
  "message": "operation succeed"
}
```

## Fallback Response Structure

If the actual API uses the previously-assumed format (unverified), the parser
must also handle:

```json
{
  "code": 1000,
  "data": {
    "capabilities": [
      {
        "serviceId": "RCE_2",
        "enabled": true,
        "version": "1.0"
      }
    ]
  }
}
```

## Parsing Contract

The integration MUST:

1. Try `data.list[]` first (APK model format)
2. Fall back to `data.capabilities[]` (legacy format)
3. Extract `functionId`/`valueEnable` from the primary format
4. Extract `serviceId`/`enabled` from the fallback format
5. Return `VehicleCapabilities` with both `capability_flags` and `service_ids`
6. On any parsing failure, return empty `VehicleCapabilities` (permissive)

## Field Reference

| JSON Field | Java Type | Required | Description |
|-----------|-----------|----------|-------------|
| `functionId` | String | Yes | Feature identifier (e.g., `"remote_control_lock"`) |
| `valueEnable` | boolean | Yes | Whether the feature is enabled |
| `functionCategory` | String | No | Grouping category |
| `name` | String | No | Human-readable name |
| `showType` | String | No | UI display type |
| `tips` | String | No | Help text |
| `valueEnum` | String | No | Comma-separated valid values |
| `valueRange` | String | No | Value range (e.g., `"16\|28"` for temp) |
| `paramsJson` | Array | No | Additional parameters |
| `configCode` | String | No | Configuration code |
| `platform` | String | No | Platform identifier |
| `priority` | Integer | No | Display priority |
| `vin` | String | No | Vehicle VIN |
| `modelCode` | String | No | Vehicle model code |
| `id` | Integer | No | Capability entry ID |
