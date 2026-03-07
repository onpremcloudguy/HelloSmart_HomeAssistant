# Data Model: Hello-Smart Foundation

**Branch**: `001-hello-smart-foundation` | **Date**: 2026-03-07

## Entities

### Account

Represents a user's Smart cloud account and associated authentication state.

| Field | Type | Description |
|-------|------|-------------|
| username | string | Email address for the Smart account |
| region | enum (EU, INTL) | Determines which auth flow and API endpoints to use |
| device_id | string | Random hex identifier generated per session (EU: 16 chars, INTL: 32 chars) |
| access_token | string | OAuth access token from initial login |
| refresh_token | string | OAuth refresh token (stored but not used — full re-login on expiry) |
| api_access_token | string | API session token used for vehicle data requests |
| api_refresh_token | string | API session refresh token (stored but not used) |
| api_user_id | string | User ID returned by the session endpoint |
| api_client_id | string (INTL only) | Client ID from INTL session response |
| expires_at | datetime | Token expiry timestamp |

**Relationships**: One Account ↔ Many Vehicles

**Validation rules**:
- `username` must be a non-empty string (email format)
- `region` must be one of EU or INTL
- `api_access_token` must be present before any vehicle API call

**State transitions**:
- `UNAUTHENTICATED` → (login flow) → `AUTHENTICATED`
- `AUTHENTICATED` → (token expired / 401 / code 1402) → `TOKEN_EXPIRED`
- `TOKEN_EXPIRED` → (re-login) → `AUTHENTICATED`
- `TOKEN_EXPIRED` → (invalid credentials) → `AUTH_FAILED`

---

### Vehicle

Represents a single Smart vehicle linked to an account.

| Field | Type | Description |
|-------|------|-------------|
| vin | string | Vehicle Identification Number (unique device identifier) |
| model_name | string | Vehicle model (e.g., "Smart #1") |
| model_year | string | Model year |
| series_code | string | Internal series code from API (e.g., "HC1H2D3B6213") |
| base_url | string | API base URL for this vehicle's data (may differ by vehicle type) |

**Relationships**: Many Vehicles ↔ One Account; One Vehicle ↔ One VehicleStatus; One Vehicle ↔ One OTAInfo

**Validation rules**:
- `vin` must be a non-empty string; used as the HA device unique identifier
- `base_url` must be a known Smart API base URL (URL allowlist validation)

---

### VehicleStatus

Point-in-time snapshot of a vehicle's state, refreshed on each polling cycle.

| Field | Type | Description |
|-------|------|-------------|
| battery_level | int (0–100) | State of charge percentage |
| range_remaining | float | Estimated remaining range in km |
| charging_state | enum | Charging status (mapped from API chargerState 0–15) |
| charger_connected | bool | Whether a charging cable is physically connected |
| charge_voltage | float (nullable) | Active charging voltage in volts |
| charge_current | float (nullable) | Active charging current in amps |
| time_to_full | int (nullable) | Minutes until fully charged |
| doors | dict[str, bool] | Per-door open/closed status (driver, passenger, rear_left, rear_right, trunk) |
| windows | dict[str, bool] | Per-window open/closed status |
| climate_active | bool | Whether climate control is running |
| latitude | float (nullable) | GPS latitude |
| longitude | float (nullable) | GPS longitude |
| last_updated | datetime | Timestamp of the data from the API |

**Validation rules**:
- `battery_level` clamped to 0–100
- `latitude` must be -90 to 90 if present; `longitude` must be -180 to 180
- `charging_state` mapped from raw API integer to a human-readable enum

**Charging state mapping** (from API `chargerState` values):
| API Value | Meaning |
|-----------|---------|
| 0 | Not charging |
| 1–3 | Charge preparation |
| 4–6 | AC charging |
| 7–9 | DC charging |
| 10–14 | Charge paused / error states |
| 15 | Fully charged |

---

### OTAInfo

Firmware update state for a vehicle.

| Field | Type | Description |
|-------|------|-------------|
| current_version | string | Current installed firmware version |
| target_version | string | Target firmware version available |
| update_available | bool | True if `target_version` != `current_version` |

**Validation rules**:
- `update_available` is derived; not stored independently
- Versions are opaque strings compared for equality only

---

## Entity-to-HA-Platform Mapping

| Data Field | HA Platform | Entity Type | Device Class |
|------------|-------------|-------------|--------------|
| battery_level | sensor | SensorEntity | battery |
| range_remaining | sensor | SensorEntity | distance |
| charging_state | sensor | SensorEntity | enum |
| charge_voltage | sensor | SensorEntity | voltage |
| charge_current | sensor | SensorEntity | current |
| time_to_full | sensor | SensorEntity | duration |
| current_version | sensor | SensorEntity | — |
| target_version | sensor | SensorEntity | — |
| charger_connected | binary_sensor | BinarySensorEntity | plug |
| update_available | binary_sensor | BinarySensorEntity | update |
| doors (per-door) | binary_sensor | BinarySensorEntity | door |
| windows (per-window) | binary_sensor | BinarySensorEntity | window |
| latitude + longitude | device_tracker | TrackerEntity | — |
