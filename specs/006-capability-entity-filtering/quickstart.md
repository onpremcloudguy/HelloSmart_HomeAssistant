# Quickstart: Capability-Based Entity Filtering

**Branch**: `006-capability-entity-filtering`

## What This Feature Does

Filters Home Assistant entity creation based on vehicle capability flags from the Smart API. Vehicles only get entities for features they actually support — no more phantom "unavailable" entities for missing features (fridge, sunroof, etc.). Also caches static vehicle data to reduce API calls.

## Key Files to Modify

| File | Change Summary |
|------|---------------|
| `custom_components/hello_smart/models.py` | Add `capability_flags` to `VehicleCapabilities`; add `StaticVehicleData` dataclass |
| `custom_components/hello_smart/api.py` | Update `async_get_capabilities()` to parse `functionId`/`valueEnable` |
| `custom_components/hello_smart/const.py` | Add `FUNCTION_ID_*` constants |
| `custom_components/hello_smart/coordinator.py` | Add `_static_cache`, fetch static data once |
| `custom_components/hello_smart/sensor.py` | Add `required_capability` to `SmartSensorEntityDescription`, filter in setup |
| `custom_components/hello_smart/binary_sensor.py` | Same pattern as sensor.py |
| `custom_components/hello_smart/switch.py` | Add `required_capability` (already has `available_fn`) |
| `custom_components/hello_smart/lock.py` | Add `required_capability` (already has `available_fn`) |
| `custom_components/hello_smart/button.py` | Add `required_capability` to description, filter in setup |
| `custom_components/hello_smart/select.py` | Add `required_capability` to description, filter in setup |
| `custom_components/hello_smart/climate.py` | Add capability check before entity creation |
| `API/endpoints/capabilities.md` | Update response schema |
| `API/entities.md` | Add capability column |
| `API/models.md` | Update VehicleCapabilities model |

## Development Workflow

```bash
# 1. Switch to feature branch
git checkout 006-capability-entity-filtering

# 2. Make changes to custom_components/hello_smart/

# 3. Deploy to dev container
docker cp custom_components/hello_smart/ ha-dev:/config/custom_components/hello_smart/

# 4. Restart HA in container
docker exec ha-dev python -m homeassistant restart

# 5. Check logs for capability parsing
docker logs ha-dev 2>&1 | grep -i "capability\|Skipping\|filtered"
```

## Critical Implementation Note

**FIRST TASK**: Capture a live API response from `/geelyTCAccess/tcservices/capability/{vin}` and log the raw JSON structure. The response schema is APK-modeled (uses `data.list[]` with `functionId`/`valueEnable`) but has never been verified against a live response. The parser should handle both the expected format and the legacy format (`data.capabilities[]` with `serviceId`/`enabled`).

## Testing Strategy

1. **Live API verification**: Capture and log actual capability response
2. **Entity count comparison**: Compare entity counts before/after with a vehicle that has all features
3. **Filtered entity verification**: Confirm entities for disabled capabilities are not created
4. **Fallback verification**: Simulate API failure and confirm all entities still created
5. **Cache verification**: Monitor API call logs across poll cycles

## Architecture Decisions

- **Permissive default**: Unknown/missing capabilities → create entity (safe fallback)
- **Opt-in filtering**: Only entities with `required_capability` set are filtered
- **In-memory cache**: Static data cached on coordinator instance, cleared on restart
- **No new files**: All changes are modifications to existing production files
