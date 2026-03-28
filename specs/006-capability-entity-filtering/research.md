# Research: Capability-Based Entity Filtering

**Branch**: `006-capability-entity-filtering` | **Date**: 2026-03-28

## Sources

| Source | Confidence |
|--------|-----------|
| APK decompiled `Capability.java` (intl + eu) | HIGH (authoritative Java model for API deserialization) |
| APK decompiled `FunctionId.java` (intl + eu) | HIGH (canonical function ID constants) |
| APK decompiled `TscVehicleCapability.java` | HIGH (Retrofit response wrapper) |
| APK Retrofit annotation `bllnew.java` | HIGH (confirms endpoint path and response type) |
| Existing integration code (`api.py`, `coordinator.py`, `models.py`) | HIGH (current behavior) |
| Spec-002 research (capability schema) | LOW — marked **SPECULATIVE** in original research |
| HA debug logs | LOW (only token-expired errors captured, no successful responses) |

---

## Research Topic 1: Capability API Response Structure

**Decision**: The actual capability API response structure uses `functionId`/`valueEnable` fields (matching the APK's `Capability.java` model), NOT the `serviceId`/`enabled`/`version` format currently assumed by the integration.

**Evidence**:

1. **APK Retrofit annotation** (`bllnew.java` line 48):
   ```java
   @GET("/geelyTCAccess/tcservices/capability/{vin}")
   Observable<BaseResult<TscVehicleCapability>> blldo(...)
   ```
   The return type `BaseResult<TscVehicleCapability>` means Gson deserializes the response into `TscVehicleCapability`.

2. **`TscVehicleCapability.java`** has two fields:
   - `List<Capability> list` — the capability entries
   - `ServiceResult serviceResult` — service metadata

3. **`Capability.java`** fields (the class Gson maps JSON to):
   - `functionId` (String) — feature identifier, e.g., `"remote_control_lock"`
   - `valueEnable` (boolean) — whether the feature is enabled
   - `functionCategory` (String) — grouping
   - `name` (String) — display name
   - `showType` (String) — UI display type
   - `tips` (String) — tooltip text
   - `valueEnum` (String) — comma-separated enum options
   - `valueRange` (String) — value range specification
   - `paramsJson` (ArrayList\<CapabilityParams>) — parameters
   - `configCode`, `platform`, `priority`, `vin`, `modelCode`, `id`, `_id`

4. **`Capability.java` does NOT have** `serviceId`, `enabled`, or `version` fields.

5. **Spec-002 research** listed the `/capability/{vin}` response schema under the **SPECULATIVE** table — inferred from Geely platform patterns, not verified against live data.

**Conclusion**: The integration's current parsing in `async_get_capabilities()` likely yields empty results:
```python
# Current (likely broken):
caps = data.get("data", {}).get("capabilities", [])  # key "capabilities" doesn't exist
service_ids = [c.get("serviceId", "") for c in caps if c.get("enabled")]  # fields don't exist
```

The correct parsing should be:
```python
# Corrected:
caps = data.get("data", {}).get("list", [])  # key "list" per TscVehicleCapability
capability_flags = {
    c.get("functionId"): c.get("valueEnable", False) for c in caps if c.get("functionId")
}
```

**Verification step required**: First implementation task MUST capture a live API response and log its structure before finalizing the parser. If the response differs from the APK model, the parser should handle both formats.

**Alternatives considered**: Trust the spec-002 speculative schema — rejected because the APK's Retrofit return type is definitive about what structure Gson expects.

---

## Research Topic 2: Function ID to Entity Mapping

**Decision**: Map APK `FunctionId.java` constants to integration entity descriptions. Only map entities that have clear functional equivalents.

**Rationale**: The APK has 114 unique function IDs. Most are status indicators or app-only features (navigation, car sharing, QR scan). The integration only needs mappings for entities it actually creates.

**Complete mapping** (function ID → integration entity):

### Remote Control Commands (buttons, locks, switches)

| Function ID | Entity Type | Platform | Integration Entity |
|------------|-------------|----------|-------------------|
| `remote_control_lock` | lock | lock.py | Door lock (lock action) |
| `remote_control_unlock` | lock | lock.py | Door lock (unlock action) |
| `remote_air_condition_switch` | climate | climate.py | Climate control |
| `remote_window_close` | button | button.py | Close windows |
| `remote_window_open` | button | button.py | Open windows |
| `remote_trunk_open` | button | button.py | Open trunk |
| `honk_flash` | button | button.py | Horn & flash |
| `remote_seat_preheat_switch` | select | select.py | Seat heating level |
| `remote_control_fragrance` | switch | switch.py | Fragrance on/off |
| `remote_appointment_charging` | time/switch | time.py, switch.py | Charging schedule |

### Status Sensors (read-only)

| Function ID | Entity Type | Platform | Integration Entity |
|------------|-------------|----------|-------------------|
| `charging_status` | sensor | sensor.py | Charging state, voltage, current, time-to-full |
| `climate_status` | sensor/binary_sensor | sensor.py, binary_sensor.py | Climate active, target temp |
| `door_lock_switch_status` | binary_sensor | binary_sensor.py | Door lock status |
| `trunk_status` | binary_sensor | binary_sensor.py | Trunk open/closed |
| `windows_rolling_status` | binary_sensor | binary_sensor.py | Window positions |
| `skylight_rolling_status` | binary_sensor | binary_sensor.py | Sunroof status |
| `tyre_pressure` | sensor | sensor.py | Tyre pressure (4 wheels) |
| `seat_heat_status` | sensor | sensor.py | Seat heating active |
| `seat_ventilation_status` | sensor | sensor.py | Seat ventilation active |
| `vehicle_position` | device_tracker | device_tracker.py | GPS location |
| `total_mileage` | sensor | sensor.py | Odometer |
| `engine_compartment_cover_status` | binary_sensor | binary_sensor.py | Hood status |
| `recharge_lid_status` | binary_sensor | binary_sensor.py | Charge port status |
| `curtain_status` | binary_sensor | binary_sensor.py | Curtain/blind status |
| `vehiecle_doors_status` | binary_sensor | binary_sensor.py | Individual door statuses |

### Unmapped (no integration entity, or always-available)

Remaining ~80 function IDs are either app-only features (navigation, car sharing, Bluetooth key, stolen car tracking) or are not represented by entities in the current integration.

**Alternatives considered**: Map every function ID including app-only features — rejected per YAGNI; only entities the integration creates need mappings.

---

## Research Topic 3: Caching Strategy for Static Data

**Decision**: Use instance variables on `SmartDataCoordinator` to cache static data after first successful fetch. Skip re-fetching on subsequent `_async_update_data` calls.

**Rationale**: Three data sources are static per vehicle session:
1. **Capabilities** — vehicle feature flags, fixed per firmware version
2. **Vehicle Ability** — visual config (images, colors, model info), fixed per vehicle spec
3. **Plant Number** — factory code, never changes

Currently all three are fetched every 60-second poll cycle (coordinator `_async_fetch_all_vehicles`). Each is an independent API call × number of vehicles.

**Implementation pattern**:
```python
class SmartDataCoordinator(DataUpdateCoordinator):
    def __init__(self, ...):
        self._static_cache: dict[str, StaticVehicleData] = {}  # keyed by VIN
    
    async def _async_fetch_all_vehicles(self, account):
        for vin in vehicle_vins:
            # Only fetch static data if not yet cached
            if vin not in self._static_cache:
                capabilities = await self._api.async_get_capabilities(...)
                ability = await self._api.async_get_vehicle_ability(...)
                plant_no = await self._api.async_get_plant_no(...)
                self._static_cache[vin] = StaticVehicleData(capabilities, ability, plant_no)
            
            # Use cached values for VehicleData construction
            cached = self._static_cache[vin]
            # ... build VehicleData with cached.capabilities, cached.ability, cached.plant_no
```

**Cache invalidation**: Cache is naturally cleared when HA restarts (coordinator re-instantiated). No manual invalidation needed — firmware updates that change capabilities require an HA restart to take effect.

**Alternatives considered**:
- HA `Store` for persistent caching — rejected; adds complexity and stale data risk on firmware updates. In-memory is sufficient since capabilities are always available from the API.
- TTL-based cache with expiry — rejected; unnecessary complexity. Capabilities don't change during a session.
- Separate one-shot setup method — rejected; the coordinator's existing `_async_update_data` flow is the right place, just with a conditional check.

---

## Research Topic 4: Entity Description Extension Pattern

**Decision**: Add an optional `required_capability: str | None` field to each entity description dataclass. When `None`, the entity is always created (opt-in filtering).

**Rationale**: Two entity platforms already have `available_fn` (switch, lock), but this is a runtime availability check (whether data exists), not a setup-time capability filter. The new `required_capability` field serves a different purpose: it gates entity *creation* during `async_setup_entry`, before the entity ever exists.

**Implementation pattern for platforms WITHOUT `available_fn`** (sensor, binary_sensor, button, select):
```python
@dataclass(frozen=True, kw_only=True)
class SmartSensorEntityDescription(SensorEntityDescription):
    value_fn: Callable[[VehicleData], Any]
    required_capability: str | None = None  # New field, opt-in
```

**Filtering logic in `async_setup_entry`** (shared across all platforms):
```python
async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for vin, vehicle_data in coordinator.data.items():
        caps = vehicle_data.capabilities
        for description in DESCRIPTIONS:
            # Capability check (FR-010 through FR-014)
            if description.required_capability and caps and caps.capability_flags:
                if not caps.capability_flags.get(description.required_capability, True):
                    _LOGGER.debug("Skipping %s: capability %s disabled", 
                                  description.key, description.required_capability)
                    continue
            # Existing available_fn check (for switch/lock platforms)
            if hasattr(description, 'available_fn') and not description.available_fn(vehicle_data):
                continue
            entities.append(SmartSensorEntity(coordinator, vin, description))
    async_add_entities(entities)
```

**Key design choice**: `caps.capability_flags.get(description.required_capability, True)` — defaults to `True` (create entity) when the function ID is not in the capability flags dict. This ensures:
- Unmapped capabilities → entity created (permissive)
- Empty capabilities (API failure) → all entities created (permissive fallback)
- Explicitly disabled capability → entity skipped

**Alternatives considered**:
- Reuse `available_fn` for capability checks — rejected; `available_fn` runs per-poll for runtime state, capability check is one-time at setup.
- Separate capability filter function — rejected; violates Simplicity principle. A single field + shared logic is simpler.
- Decorator pattern on entity descriptions — rejected; over-engineering for a simple flag check.

---

## Research Topic 5: Fridge Feature — Function ID Discovery

**Decision**: The fridge feature does NOT have a corresponding `FunctionId.java` constant. The fridge is gated by service ID `"UFR"` (already defined as `SERVICE_ID_FRIDGE` in `const.py`), not by a function ID.

**Evidence**: Searched both EU and INTL decompiled FunctionId.java for "fridge" — no matches. The integration currently uses `SERVICE_ID_FRIDGE = "UFR"` for command service identification.

**Implication**: For fridge entities, the capability check should use the **service ID** path (check if `"UFR"` is in `service_ids`) rather than the function ID path. This means the `required_capability` field needs to support both function IDs and service IDs, OR the fridge uses the existing `available_fn` pattern (data is `None` when unsupported).

**Decision**: Use the existing `available_fn` pattern for fridge — `available_fn=lambda data: data.fridge is not None`. This already works because the fridge status endpoint returns an error/empty for vehicles without a fridge, resulting in `fridge=None` in VehicleData. No additional capability check needed.

**Alternatives considered**: Add a dual-mode `required_capability` supporting both function IDs and service IDs — rejected; increases complexity for a single edge case that's already handled.

---

## Research Topic 6: API Documentation Gap Analysis

**Decision**: Three documentation files need updates to reflect the actual capability response structure.

| File | Current State | Required Update |
|------|--------------|-----------------|
| `API/endpoints/capabilities.md` | Shows speculative `serviceId`/`enabled`/`version` schema | Replace with `functionId`/`valueEnable` schema from Capability.java; note that schema is APK-modeled and requires live verification |
| `API/entities.md` | Entity table with no capability column | Add `Required Capability` column with function IDs |
| `API/models.md` | `VehicleCapabilities` has only `service_ids` | Add `capability_flags: dict[str, bool]` field documentation |

**Alternatives considered**: Create a separate capability mapping document — rejected; the information fits naturally in the existing entity mapping table.
