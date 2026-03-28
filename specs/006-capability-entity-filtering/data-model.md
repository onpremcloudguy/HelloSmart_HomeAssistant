# Data Model: Capability-Based Entity Filtering

**Branch**: `006-capability-entity-filtering` | **Date**: 2026-03-28

---

## Entity Relationship Diagram

```
┌─────────────────────────────────┐
│         VehicleData             │
│  (existing, per-VIN)            │
├─────────────────────────────────┤
│  vehicle: Vehicle               │
│  status: VehicleStatus          │
│  capabilities: VehicleCapabili… │──┐
│  ability: VehicleAbility        │  │
│  ...                            │  │
└─────────────────────────────────┘  │
                                     │
    ┌────────────────────────────────┘
    ▼
┌─────────────────────────────────┐
│     VehicleCapabilities         │
│  (MODIFIED)                     │
├─────────────────────────────────┤
│  service_ids: list[str]         │  ← existing (backward compat)
│  capability_flags: dict[str,    │  ← NEW: functionId → valueEnable
│                     bool]       │
└─────────────────────────────────┘
         ▲
         │ populated from API response
         │
┌─────────────────────────────────┐
│  Capability API Response        │
│  (per TscVehicleCapability)     │
├─────────────────────────────────┤
│  data.list[]:                   │
│    functionId: str              │
│    valueEnable: bool            │
│    functionCategory: str        │
│    name: str                    │
│    valueEnum: str               │
│    valueRange: str              │
│    paramsJson: list[Params]     │
│    configCode: str              │
│    platform: str                │
│    priority: int                │
│    showType: str                │
│    tips: str                    │
└─────────────────────────────────┘

┌─────────────────────────────────┐       ┌──────────────────────────────┐
│  StaticVehicleData              │       │  SmartDataCoordinator        │
│  (NEW, cached per-VIN)          │       │  (MODIFIED)                  │
├─────────────────────────────────┤       ├──────────────────────────────┤
│  capabilities: VehicleCapabili… │       │  _static_cache:              │
│  ability: VehicleAbility | None │       │    dict[str, StaticVehicle…] │
│  plant_no: str                  │       │                              │
└─────────────────────────────────┘       └──────────────────────────────┘

┌─────────────────────────────────┐
│  Entity Description Dataclass   │
│  (MODIFIED — all platforms)     │
├─────────────────────────────────┤
│  key: str                       │  ← existing
│  value_fn / is_on_fn / etc.     │  ← existing (platform-specific)
│  required_capability: str|None  │  ← NEW: function ID that must be enabled
└─────────────────────────────────┘

┌─────────────────────────────────┐
│  CAPABILITY_MAP (const.py)      │
│  (NEW, static lookup)           │
├─────────────────────────────────┤
│  Maps entity description keys   │
│  to function ID strings.        │
│  Used to populate               │
│  required_capability on entity  │
│  descriptions at definition     │
│  time.                          │
└─────────────────────────────────┘
```

---

## Modified Models

### VehicleCapabilities (models.py)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `service_ids` | `list[str]` | `[]` | Existing. List of enabled service IDs (backward compat) |
| `capability_flags` | `dict[str, bool]` | `{}` | NEW. Maps `functionId` → `valueEnable`. Populated from API response `data.list[]` |

### StaticVehicleData (models.py — NEW)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `capabilities` | `VehicleCapabilities \| None` | `None` | Cached capability flags |
| `ability` | `VehicleAbility \| None` | `None` | Cached vehicle visual config |
| `plant_no` | `str` | `""` | Cached factory plant number |

### Entity Description Extension (all platforms)

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `required_capability` | `str \| None` | `None` | Function ID from `FunctionId.java` that must be enabled for this entity to be created. `None` = always create. |

---

## Capability-to-Entity Mapping (const.py)

```
FUNCTION_ID_REMOTE_LOCK          = "remote_control_lock"
FUNCTION_ID_REMOTE_UNLOCK        = "remote_control_unlock"
FUNCTION_ID_CLIMATE              = "remote_air_condition_switch"
FUNCTION_ID_WINDOW_CLOSE         = "remote_window_close"
FUNCTION_ID_WINDOW_OPEN          = "remote_window_open"
FUNCTION_ID_TRUNK_OPEN           = "remote_trunk_open"
FUNCTION_ID_HONK_FLASH           = "honk_flash"
FUNCTION_ID_SEAT_HEAT            = "remote_seat_preheat_switch"
FUNCTION_ID_SEAT_VENT            = "seat_ventilation_status"
FUNCTION_ID_FRAGRANCE            = "remote_control_fragrance"
FUNCTION_ID_CHARGING             = "charging_status"
FUNCTION_ID_DOOR_STATUS          = "door_lock_switch_status"
FUNCTION_ID_TRUNK_STATUS         = "trunk_status"
FUNCTION_ID_WINDOW_STATUS        = "windows_rolling_status"
FUNCTION_ID_SKYLIGHT_STATUS      = "skylight_rolling_status"
FUNCTION_ID_TYRE_PRESSURE        = "tyre_pressure"
FUNCTION_ID_VEHICLE_POSITION     = "vehicle_position"
FUNCTION_ID_TOTAL_MILEAGE        = "total_mileage"
FUNCTION_ID_HOOD_STATUS          = "engine_compartment_cover_status"
FUNCTION_ID_CHARGE_PORT_STATUS   = "recharge_lid_status"
FUNCTION_ID_CURTAIN_STATUS       = "curtain_status"
FUNCTION_ID_DOORS_STATUS         = "vehiecle_doors_status"
FUNCTION_ID_CLIMATE_STATUS       = "climate_status"
FUNCTION_ID_CHARGING_RESERVATION = "remote_appointment_charging"
```

---

## Filtering Logic Flow

```
async_setup_entry():
  for each VIN in coordinator.data:
    vehicle_data = coordinator.data[VIN]
    caps = vehicle_data.capabilities
    
    for each entity_description in DESCRIPTIONS:
      ┌─ Has required_capability? ─── No ──→ CREATE entity (always)
      │
      Yes
      │
      ├─ caps is None or caps.capability_flags empty? ── Yes ──→ CREATE entity (permissive fallback)
      │
      No
      │
      ├─ required_capability in caps.capability_flags? ── No ──→ CREATE entity (unknown cap = permissive)
      │
      Yes
      │
      ├─ caps.capability_flags[required_capability] is True? ── Yes ──→ CREATE entity
      │
      No
      │
      └─ SKIP entity (capability explicitly disabled)
         Log: "Skipping {key}: capability {func_id} disabled"
```

---

## State Transitions

### Static Data Cache Lifecycle

```
HA Start → Coordinator.__init__()
  _static_cache = {}  (empty)

First poll → _async_update_data() → _async_fetch_all_vehicles()
  Per VIN: fetch capabilities, ability, plant_no from API
  Store in _static_cache[vin] = StaticVehicleData(...)
  Build VehicleData using cached values

Subsequent polls → _async_update_data() → _async_fetch_all_vehicles()
  Per VIN: _static_cache[vin] exists → skip API calls
  Build VehicleData using cached values

HA Restart → Coordinator.__init__()
  _static_cache = {}  (cleared, re-fetched on first poll)
```

---

## Validation Rules

| Rule | Applies To | Behavior |
|------|-----------|----------|
| Missing `functionId` in capability object | API parsing | Skip entry, log debug warning |
| Empty capability list from API | Entity filtering | Permissive fallback (create all) |
| API call failure | Entity filtering | Permissive fallback (create all) |
| `required_capability` is `None` | Entity creation | Always create (opt-in filtering) |
| Function ID not in capability flags dict | Entity creation | Create entity (unknown = permitted) |
| Function ID in flags and `False` | Entity creation | Skip entity |
