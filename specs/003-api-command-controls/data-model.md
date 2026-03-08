# Data Model: API Command Controls

**Feature**: 003-api-command-controls  
**Date**: 2025-07-24  
**Depends on**: Existing models from `custom_components/hello_smart/models.py`

---

## New Entities

### CommandResult

Represents the outcome of a single vehicle command.

| Field | Type | Description |
|-------|------|-------------|
| `success` | `bool` | Whether the API accepted the command |
| `service_id` | `str` | Service ID that was sent (e.g., `"RDL_2"`) |
| `timestamp` | `datetime` | When the command was sent |
| `error_message` | `str \| None` | Error description if `success` is `False` |

**Used by**: All command methods in `api.py` to return a uniform result. Not persisted — ephemeral per command invocation.

**Validation**:
- `service_id` must be a non-empty string
- `timestamp` is set at command-send time

---

### CommandPayload

Represents the serializable JSON payload sent to the telematics PUT endpoint.

| Field | Type | Description |
|-------|------|-------------|
| `creator` | `str` | Always `"tc"` |
| `command` | `str` | `"start"` or `"stop"` |
| `service_id` | `str` | The service ID (e.g., `"RCE_2"`, `"rcs"`, `"RDL_2"`) |
| `timestamp` | `str` | Epoch milliseconds as string |
| `operation_scheduling` | `OperationScheduling` | Scheduling parameters |
| `service_parameters` | `list[ServiceParameter]` | Command-specific key/value pairs |

**Note**: This is a logical model — the actual implementation will use a `dict` to match the JSON payload directly, following pySmartHashtag's pattern. No dataclass is needed.

---

### ServiceParameter

Key/value pair within a command payload.

| Field | Type | Description |
|-------|------|-------------|
| `key` | `str` | Parameter key (e.g., `"rce.temp"`, `"operation"`) |
| `value` | `str` | Parameter value, always a string (e.g., `"22.0"`, `"1"`) |

---

### OperationScheduling

Scheduling configuration within a command payload.

| Field | Type | Description |
|-------|------|-------------|
| `duration` | `int` | Duration in minutes (180 for climate, 6 for charging) |
| `interval` | `int` | Always `0` for immediate commands |
| `occurs` | `int` | Always `1` for single execution |
| `recurrent_operation` | `bool \| int` | Always `False`/`0` for immediate commands |
| `scheduled_time` | `str \| None` | `None` for immediate, ISO time for scheduled |

---

## Modified Entities

### VehicleData (existing — add field)

Add a `last_command_time` field to support per-vehicle command cooldown.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `last_command_time` | `datetime \| None` | `None` | Timestamp of last command sent; used for 5-second cooldown enforcement |

**Rationale**: The cooldown timer needs to persist across command invocations but resets on each coordinator refresh cycle. Storing it on `VehicleData` keeps it scoped per vehicle.

---

## Existing Entities Used (No Changes)

These existing models already have all the fields needed for command state tracking and optimistic updates:

| Entity | Relevant Fields | Command Usage |
|--------|----------------|---------------|
| `VehicleStatus` | `doors`, `windows`, `climate_active`, `charging_state`, `charger_connected` | Optimistic update targets after lock/climate/charging/window commands |
| `VtmSettings` | `enabled` | Optimistic update target after VTM toggle |
| `FridgeStatus` | `active` | Optimistic update target after fridge toggle |
| `FragranceDetails` | `active` | Optimistic update target after fragrance toggle |
| `LockerStatus` | `locked` | Optimistic update target after locker lock/unlock |
| `ChargingReservation` | `start_time`, `end_time`, `target_soc` | Optimistic update for schedule changes |
| `ClimateSchedule` | `enabled`, `scheduled_time`, `temperature` | Optimistic update for schedule changes |

---

## Enum Additions

### ServiceId (new)

String enum for known command service IDs.

| Value | Constant | Description |
|-------|----------|-------------|
| `"RDL_2"` | `DOOR_LOCK` | Remote door lock |
| `"RDU_2"` | `DOOR_UNLOCK` | Remote door unlock |
| `"RCE_2"` | `CLIMATE` | Remote climate/environment control |
| `"rcs"` | `CHARGING` | Remote charging start/stop |
| `"RHL"` | `HORN_LIGHT` | Remote horn and light (find my car) |
| `"RWS_2"` | `WINDOW_SET` | Remote window set (close) |
| `"UFR"` | `FRIDGE` | Fridge on/off |
| `"RSH"` | `SEAT_HEAT` | Remote seat heat |

**Note**: Some service IDs may be adjusted during implementation testing. Unknown/unverified IDs are not included until confirmed.

---

## State Transitions

### Door Lock Entity

```
locked ──[unlock command]──→ unlocked (optimistic)
                              ├──[refresh confirms]──→ unlocked (confirmed)
                              └──[refresh shows locked]──→ locked (reverted)

unlocked ──[lock command]──→ locked (optimistic)
                              ├──[refresh confirms]──→ locked (confirmed)
                              └──[refresh shows unlocked]──→ unlocked (reverted)
```

### Climate Entity

```
off ──[start command (temp=22°C)]──→ heating (optimistic)
                                      ├──[refresh confirms]──→ heating (confirmed)
                                      └──[refresh shows off]──→ off (reverted)

heating ──[stop command]──→ off (optimistic)
                            ├──[refresh confirms]──→ off (confirmed)
                            └──[refresh shows heating]──→ heating (reverted)
```

### Charging Switch

```
off ──[start command]──→ on (optimistic)
                          ├──[refresh confirms]──→ on (confirmed)
                          └──[command fails / no charger]──→ off (reverted)

on ──[stop command]──→ off (optimistic)
```

### Button Entities (horn, flash, find, close windows)

```
idle ──[press]──→ command sent ──→ idle (no state to track)
                                   └──[error]──→ error notification
```

---

## Relationships

```
VehicleData (1)
  ├── VehicleStatus (1) ← optimistic updates from commands
  ├── VtmSettings (0..1) ← optimistic update from VTM toggle
  ├── FridgeStatus (0..1) ← optimistic update from fridge toggle
  ├── FragranceDetails (0..1) ← optimistic update from fragrance toggle
  ├── LockerStatus (0..1) ← optimistic update from locker lock/unlock
  ├── ChargingReservation (0..1) ← update from schedule time changes
  ├── ClimateSchedule (0..1) ← update from schedule time/toggle changes
  └── last_command_time ← cooldown tracking

SmartAPI (1)
  ├── async_send_command(vin, payload) → CommandResult
  ├── async_set_charging_reservation(vin, data) → CommandResult
  └── async_set_climate_schedule(vin, data) → CommandResult

SmartDataCoordinator (1)
  ├── async_send_vehicle_command(vin, service_id, ...) → handles select + send + optimistic + delayed refresh
  └── _command_cooldown: dict[str, datetime] tracks per-VIN cooldown
```

---

## HA Platform Entity Mapping

| HA Platform | Entity | Underlying Model Field | Service ID |
|------------|--------|----------------------|------------|
| `lock` | Door Lock | `VehicleStatus.doors` | `RDL_2` / `RDU_2` |
| `lock` | Trunk Locker | `LockerStatus.locked` | TBD |
| `climate` | Climate Control | `VehicleStatus.climate_active` + temp | `RCE_2` |
| `switch` | Charging | `VehicleStatus.charging_state` | `rcs` |
| `switch` | Fridge | `FridgeStatus.active` | `UFR` |
| `switch` | Fragrance | `FragranceDetails.active` | TBD |
| `switch` | VTM | `VtmSettings.enabled` | TBD |
| `switch` | Climate Schedule | `ClimateSchedule.enabled` | Schedule endpoint |
| `button` | Horn | N/A (momentary) | `RHL` |
| `button` | Flash Lights | N/A (momentary) | `RHL` |
| `button` | Find My Car | N/A (momentary) | `RHL` |
| `button` | Close Windows | N/A (momentary) | `RWS_2` |
| `number` | Target SOC | `ChargingReservation.target_soc` | Schedule endpoint |
| `time` | Charging Start Time | `ChargingReservation.start_time` | Schedule endpoint |
| `time` | Charging End Time | `ChargingReservation.end_time` | Schedule endpoint |
| `time` | Climate Schedule Time | `ClimateSchedule.scheduled_time` | Schedule endpoint |
