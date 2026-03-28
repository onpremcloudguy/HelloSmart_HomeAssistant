# Capabilities

Feature flags indicating which services and functions are enabled for the vehicle.

[← Back to API Reference](../README.md) · [Common Patterns](../common-patterns.md)

---

## Request

```http
GET {base_url}/geelyTCAccess/tcservices/capability/{vin}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| `vin` | Path | Yes | Vehicle VIN |

### Headers

Standard [signed headers](../common-patterns.md#required-headers) with `authorization` token.

---

## Response

The API returns capability data in one of two formats. The integration detects and parses both.

### Primary Format: `data.list[]` (APK Model)

Based on the APK `Capability.java` / `TscVehicleCapability` Retrofit model:

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
        "showType": 1,
        "tips": "",
        "valueEnum": "",
        "valueRange": "",
        "paramsJson": "",
        "configCode": "",
        "platform": "TSP",
        "priority": 1
      },
      {
        "functionId": "charging_status",
        "valueEnable": true,
        "functionCategory": "vehicle_status",
        "name": "Charging Status",
        "showType": 1
      }
    ]
  }
}
```

#### Capability Entry (Primary)

| Field | Type | Description |
|-------|------|-------------|
| `functionId` | string | Function identifier (e.g., `"remote_control_lock"`, `"charging_status"`) |
| `valueEnable` | bool | Whether the function is enabled for this vehicle |
| `functionCategory` | string | Category grouping (e.g., `"remote_control"`, `"vehicle_status"`) |
| `name` | string | Human-readable name |
| `showType` | int | Display type hint from app UI |
| `tips` | string | Tooltip text (often empty) |
| `valueEnum` | string | Enum value options (if applicable) |
| `valueRange` | string | Valid value range (if applicable) |
| `paramsJson` | string | Additional parameters as JSON string |
| `configCode` | string | Configuration code |
| `platform` | string | Source platform (e.g., `"TSP"`) |
| `priority` | int | Sort priority |

### Fallback Format: `data.capabilities[]` (Legacy)

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

#### Capability Entry (Legacy)

| Field | Type | Description |
|-------|------|-------------|
| `serviceId` | string | Service identifier (e.g., `"RCE_2"`, `"FOTA"`) |
| `enabled` | bool | Whether the service is active |
| `version` | string | Service API version |

---

## Data Model

Returns: [`VehicleCapabilities`](../models.md#vehiclecapabilities)

| Model Field | Source |
|-------------|--------|
| `capability_flags` | Dict of `functionId` → `valueEnable` from primary format |
| `service_ids` | List of `serviceId` values where `enabled == true` (legacy format, or `serviceId` from primary if present) |

### Function ID Reference

These function IDs are used for entity filtering (defined in `const.py`):

| Constant | `functionId` Value | Controls |
|----------|--------------------|----------|
| `FUNCTION_ID_REMOTE_LOCK` | `remote_control_lock` | Lock entity |
| `FUNCTION_ID_REMOTE_UNLOCK` | `remote_control_unlock` | (paired with lock) |
| `FUNCTION_ID_CLIMATE` | `remote_air_condition_switch` | Climate entity |
| `FUNCTION_ID_WINDOW_CLOSE` | `remote_window_close` | Close windows button |
| `FUNCTION_ID_WINDOW_OPEN` | `remote_window_open` | (future: open windows) |
| `FUNCTION_ID_TRUNK_OPEN` | `remote_trunk_open` | (future: trunk button) |
| `FUNCTION_ID_HONK_FLASH` | `honk_flash` | Horn, flash, find-my-car buttons |
| `FUNCTION_ID_SEAT_HEAT` | `remote_seat_preheat_switch` | Seat heating sensors & selects |
| `FUNCTION_ID_SEAT_VENT` | `seat_ventilation_status` | Seat ventilation sensors & selects |
| `FUNCTION_ID_FRAGRANCE` | `remote_control_fragrance` | Fragrance switch & sensors |
| `FUNCTION_ID_CHARGING` | `charging_status` | Charging sensors (voltage, current, etc.) |
| `FUNCTION_ID_DOOR_STATUS` | `door_lock_switch_status` | Door lock binary sensors |
| `FUNCTION_ID_TRUNK_STATUS` | `trunk_status` | Trunk binary sensor |
| `FUNCTION_ID_WINDOW_STATUS` | `windows_rolling_status` | Window binary sensors |
| `FUNCTION_ID_SKYLIGHT_STATUS` | `skylight_rolling_status` | Sunroof binary sensor |
| `FUNCTION_ID_TYRE_PRESSURE` | `tyre_pressure` | Tyre pressure/temp sensors & warnings |
| `FUNCTION_ID_VEHICLE_POSITION` | `vehicle_position` | (future: device tracker) |
| `FUNCTION_ID_TOTAL_MILEAGE` | `total_mileage` | Odometer sensor |
| `FUNCTION_ID_HOOD_STATUS` | `engine_compartment_cover_status` | Engine hood binary sensor |
| `FUNCTION_ID_CHARGE_PORT_STATUS` | `recharge_lid_status` | Charge lid binary sensors |
| `FUNCTION_ID_CURTAIN_STATUS` | `curtain_status` | Curtain binary sensors |
| `FUNCTION_ID_DOORS_STATUS` | `vehiecle_doors_status` | Door open/close binary sensors (note: typo in APK) |
| `FUNCTION_ID_CLIMATE_STATUS` | `remote_air_condition_status` | Climate schedule sensors |
| `FUNCTION_ID_CHARGING_RESERVATION` | `recharge_appointment` | Charging schedule entities |

---

## Parsing Strategy

The integration uses a dual-format parser:

1. **Primary**: Try `data.list[]` with `functionId`/`valueEnable` fields
2. **Fallback**: Try `data.capabilities[]` with `serviceId`/`enabled` fields
3. **Empty**: If neither format has data, return empty `VehicleCapabilities`

This ensures backward compatibility if the API format changes between regions or firmware versions.

### V2 → V1 Function ID Mapping

The API may return **v2 capability IDs** (with `_2` suffix or renamed keys) while the integration's entity descriptions reference the **v1 function IDs** from the APK's original `FunctionId.java`. The integration propagates v2 values to their v1 aliases so entity filtering works regardless of API version.

| V2 API Key (returned by API) | V1 Alias(es) (used by entities) |
|------------------------------|-------------------------------|
| `charging_status_2` | `charging_status` |
| `remote_climate_control_2` | `remote_air_condition_switch`, `climate_status` |
| `curtain_status_2` | `curtain_status` |
| `sunroof_automatic_close` | `skylight_rolling_status` |
| `recharge_lid_status_2` | `recharge_lid_status` |
| `remote_control_lock_2` | `remote_control_lock` |
| `remote_control_unlock_2` | `remote_control_unlock` |
| `remote_control_window_2` | `remote_window_close`, `remote_window_open` |
| `remote_control_ventilate_2` | `seat_ventilation_status` |
| `tire_pressure_warning_2` | `tyre_pressure` |

### Inferred Capabilities

Some v1 function IDs have no direct v2 equivalent in the API response. These are inferred from related capabilities:

| V1 Function ID | Inferred From | Logic |
|----------------|---------------|-------|
| `remote_control_fragrance` | `fragrance_exhausted_warning_2` | If fragrance warning exists → fragrance control is available |
| `remote_seat_preheat_switch` | `remote_climate_control_2` | If climate control exists → seat preheat is available |
| `remote_trunk_open` | `trunk_status` | If trunk status exists → trunk open is available |

### Default Behaviour

When a `functionId` is **not present** in the capability flags (neither directly nor via mapping), the integration defaults to `False` — meaning the entity is **not created**. This matches the APK's behaviour where missing capabilities indicate the feature is unavailable.

> **Note:** Earlier versions defaulted to `True` (fail-open), which caused entities to appear for unsupported features. The current default of `False` is deliberate and matches the APK's `FunctionId` checking logic.

---

## Related Entities

| Entity | Platform | Device Class |
|--------|----------|-------------|
| `capability_count` | sensor | — |

---

## Notes

- Capability flags are fetched **once per session** and cached in `_static_cache` to reduce API calls
- When a `functionId` has `valueEnable: false`, all entities requiring that capability are not created
- If capabilities cannot be fetched, all entities default to being created (fail-open)
- The integration preserves the APK's typo in `vehiecle_doors_status` to match the actual API response
- The API currently returns **89 capability entries**, all set to `true` — meaning capability-based filtering alone may not be sufficient for all vehicles
- For hardware-level filtering (e.g., sunroof not installed), see the [sentinel value documentation](vehicle-status.md#sentinel-value-101-not-equipped)
- For trim-level filtering (e.g., Pure trim lacks seat heating), see the [edition feature matrix](list-vehicles.md#edition-feature-matrix)

---

## Related

- Source: [`api.py → async_get_capabilities()`](../../custom_components/hello_smart/api.py)
- APK source: `Capability.java`, `TscVehicleCapability.java` (Retrofit model)
