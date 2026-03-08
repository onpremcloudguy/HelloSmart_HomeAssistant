# Quickstart: API Command Controls

**Feature**: 003-api-command-controls  
**Audience**: Developer implementing the tasks from this plan

---

## Overview

This feature adds vehicle command capabilities to the Hello Smart HA integration. All commands use a single PUT endpoint (`/remote-control/vehicle/telematics/{vin}`) with different `serviceId` values to control what action the vehicle takes. Schedule updates use dedicated PUT endpoints.

## Architecture at a Glance

```
User presses HA control
        │
        ▼
  Entity platform (lock.py, climate.py, switch.py, button.py, etc.)
        │
        ▼
  coordinator.async_send_vehicle_command(vin, service_id, command, params)
        │
        ├── Cooldown check (5s per VIN)
        ├── async_select_vehicle(vin)
        ├── api.async_send_command(vin, payload)  →  PUT /telematics/{vin}
        │
        ▼
  On success:
        ├── Optimistic update → coordinator's VehicleData
        ├── async_write_ha_state() → instant UI feedback
        └── Delayed coordinator.async_request_refresh() (5–10s) → confirm actual state
```

## Key Files to Modify

| File | Changes |
|------|---------|
| `api.py` | Add `async_send_command()` for telematics PUT, schedule PUT methods |
| `coordinator.py` | Add `async_send_vehicle_command()` orchestrator with cooldown, optimistic updates, delayed refresh |
| `models.py` | Add `CommandResult` dataclass, `ServiceId` enum, `last_command_time` to `VehicleData` |
| `const.py` | Add service ID constants, command-related URL paths |
| `__init__.py` | Add new platforms: `LOCK`, `CLIMATE`, `SWITCH`, `BUTTON`, `NUMBER`, `TIME` |
| `strings.json` | Add translation keys for all new entities |

## New Files to Create

| File | Purpose |
|------|---------|
| `lock.py` | Door lock + trunk locker entities |
| `climate.py` | Climate pre-conditioning entity |
| `switch.py` | Charging, fridge, fragrance, VTM, climate schedule toggle entities |
| `button.py` | Horn, flash, find-my-car, close-windows entities |
| `number.py` | Target SOC slider entity |
| `time.py` | Charging schedule start/end, climate schedule time entities |

## Command Payload Pattern

Every command follows this template:

```python
payload = {
    "creator": "tc",
    "command": "start",  # or "stop"
    "serviceId": "RDL_2",  # varies per command
    "timestamp": str(int(time.time() * 1000)),
    "operationScheduling": {
        "duration": 6,
        "interval": 0,
        "occurs": 1,
        "recurrentOperation": False,
    },
    "serviceParameters": [
        {"key": "operation", "value": "1"},
    ],
}
body = json.dumps(payload, separators=(",", ":"))  # no spaces
```

## Implementation Order

1. **Command infrastructure** — `api.py` PUT method, `coordinator.py` orchestrator, `models.py` additions
2. **Lock platform** (P1) — most common, validates the full command pipeline
3. **Climate platform** (P2) — validated by pySmartHashtag reference
4. **Switch platform** (P3 charging) — also validated by pySmartHashtag reference
5. **Button platform** (P4 alerts) — simplest, no state tracking
6. **Number + Time platforms** (P3 SOC, P8 schedules) — schedule endpoints
7. **Remaining switches** (P5/P7 accessories, VTM)
8. **Window close button** (P6) — needs verification

## Gotchas

1. **Charging `serviceId` is lowercase** `"rcs"` — all others are uppercase
2. **Charging uses `timeStamp`** (capital S) — all others use `timestamp`
3. **Charging `command` is always `"start"`** — even for stop; the `serviceParameters` determine the action
4. **JSON body must have no spaces** — use `json.dumps(payload, separators=(",", ":"))`
5. **HMAC signature includes the body** — the PUT body must be passed to `build_signed_headers()`
6. **`async_select_vehicle()` must precede every command** — establishes the vehicle session
7. **Response format may differ from GET endpoints** — commands return `{"success": true}` not `{"code": 1000, ...}`
8. **Dynamic entity visibility** — only create command entities when the corresponding GET endpoint returns data (e.g., no fridge switch if `fridge` is `None` in `VehicleData`)
