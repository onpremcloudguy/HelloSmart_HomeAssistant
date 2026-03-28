# Feature Specification: Capability-Based Entity Filtering

**Feature Branch**: `006-capability-entity-filtering`
**Created**: 2025-05-25
**Status**: Draft
**Input**: User description: "Implement capability-based entity filtering using the vehicle capability API to only register entities for features the vehicle actually supports, cache static data, and update API documentation."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Only See Entities My Vehicle Supports (Priority: P1)

As a Home Assistant user with a Smart vehicle, I want the integration to only create entities for features my vehicle actually supports so that my dashboard is clean and free of phantom entities that show "unavailable" or "unknown" states.

**Why this priority**: This is the core value of the feature. Users currently see dozens of entities for features their vehicle does not have (e.g., fridge controls on a vehicle without a fridge, sunroof controls on a vehicle without a sunroof). These phantom entities create confusion, clutter dashboards, and generate spurious "unavailable" log warnings.

**Independent Test**: Can be fully tested by configuring the integration with a vehicle that lacks certain features (e.g., no fridge, no sunroof) and verifying that only entities corresponding to enabled capability flags are created. Delivers immediate value by eliminating phantom entities.

**Acceptance Scenarios**:

1. **Given** a vehicle that does NOT support the fridge feature (capability flag `vehicle_fridge` is `false` or absent), **When** the integration loads, **Then** no fridge-related entities (fridge switch, fridge temperature sensor) are created.
2. **Given** a vehicle that DOES support remote door lock/unlock (capability flag `remote_control_lock` is `true`), **When** the integration loads, **Then** the door lock entity is created and functional.
3. **Given** a vehicle where the capability API returns a subset of enabled features, **When** the user views the Home Assistant entity list, **Then** only entities matching enabled capabilities appear — no "unavailable" or "unknown" phantom entities exist.
4. **Given** a vehicle with all common features enabled (climate, locks, windows, charging), **When** the integration loads, **Then** all corresponding entities are created and behave identically to the current integration (no regression).

---

### User Story 2 - Command Controls Respect Capabilities (Priority: P2)

As a Home Assistant user, I want command-based entities (lock/unlock, climate start/stop, window open/close, horn/flash) to only appear if my vehicle's capability flags indicate the vehicle supports those remote control operations, so I don't accidentally send unsupported commands.

**Why this priority**: Command entities that target unsupported operations produce confusing error responses from the API. Filtering commands by capability prevents user frustration and reduces unnecessary API calls.

**Independent Test**: Can be tested by checking that a vehicle without remote window control capability does not expose window open/close button entities, and that sending commands through enabled entities succeeds as before.

**Acceptance Scenarios**:

1. **Given** a vehicle whose capability flags include `remote_window_close` as enabled, **When** the integration loads, **Then** the window close button entity is created.
2. **Given** a vehicle whose capability flags do NOT include `remote_trunk_open`, **When** the integration loads, **Then** no trunk open button entity is created.
3. **Given** a vehicle with climate control capabilities enabled, **When** the user activates the climate entity, **Then** the command executes successfully (no regression from current behavior).

---

### User Story 3 - Reduced API Calls for Static Data (Priority: P3)

As an integration maintainer, I want static vehicle data (capabilities, vehicle ability/visual config, plant number) to be fetched only once during setup and cached, rather than re-fetched every polling cycle, so that the integration makes fewer API calls and initializes faster on subsequent polls.

**Why this priority**: Currently, capabilities, vehicle ability, and plant number are fetched on every 60-second poll cycle despite being static data that doesn't change during a vehicle's lifetime. Caching eliminates redundant API calls, reduces load on the Smart cloud API, and speeds up each poll cycle.

**Independent Test**: Can be tested by monitoring API call logs during multiple poll cycles and confirming that capability, vehicle ability, and plant number endpoints are called only once during initial setup and not repeated on subsequent polls.

**Acceptance Scenarios**:

1. **Given** the integration has completed its initial setup and fetched capabilities, **When** the next polling cycle runs, **Then** the capability endpoint is NOT called again.
2. **Given** the integration has cached vehicle ability data, **When** the coordinator performs a data update, **Then** vehicle ability data is served from cache without an API call.
3. **Given** the integration is restarted (Home Assistant restart), **When** it initializes, **Then** capabilities, vehicle ability, and plant number are fetched fresh and cached again.

---

### User Story 4 - Accurate API Documentation (Priority: P4)

As a contributor or developer working on the integration, I want the API documentation to accurately describe the capability endpoint response structure (including `functionId`, `valueEnable`, and related fields) and the mapping between capability flags and entities, so that future development is well-informed.

**Why this priority**: The current API documentation does not reflect the full capability response structure. Updated documentation reduces onboarding time for contributors and prevents repeated reverse-engineering of the APK.

**Independent Test**: Can be tested by reviewing the documentation files and confirming they contain the full capability response schema, function ID mappings, and entity-to-capability relationships.

**Acceptance Scenarios**:

1. **Given** a contributor reads the capabilities endpoint documentation, **When** they look for the response schema, **Then** they find the complete structure including `functionId`, `valueEnable`, `functionCategory`, `paramsJson`, and other fields.
2. **Given** a contributor wants to add a new entity, **When** they consult the entity documentation, **Then** they find guidance on how to associate a new entity with a capability flag.

---

### Edge Cases

- What happens when the capability API is unreachable or returns an error during initial setup? The integration should fall back to creating all entities (permissive default) and log a warning, so users are not left with zero entities.
- What happens when the capability API returns an empty capabilities list? Same permissive fallback — create all entities and log a warning indicating capabilities could not be determined.
- What happens when a capability flag's `functionId` does not match any known entity mapping? The unmapped capability is ignored (no entity is created for it), and a debug log entry records the unknown function ID for future investigation.
- What happens when a new entity description is added to the code but no capability mapping is defined for it? The entity should be created unconditionally (opt-in filtering), so that new entities work immediately and capability mapping can be added later.
- What happens if the capability response structure changes (e.g., field names differ between API versions)? The parser should handle missing fields gracefully and fall back to permissive entity creation with a logged warning.
- What happens when a vehicle's capabilities change (e.g., after a firmware update that enables a new feature)? Since capabilities are cached per session, the new capability will be picked up on the next Home Assistant restart.

## Assumptions

- The capability endpoint (`/geelyTCAccess/tcservices/capability/{vin}`) returns a list of capability objects, each containing at minimum `functionId` (string) and `valueEnable` (boolean), matching the structure observed in the decompiled APK (`Capability.java`).
- The APK's `FunctionId.java` constants (126 function IDs) represent the canonical list of capability identifiers used by the Smart cloud API.
- Capability flags are static for a vehicle's current firmware version and do not change between polling intervals. They may change after OTA firmware updates, but this is handled by restarting Home Assistant.
- The existing `serviceId` field in capability objects is unrelated to `functionId` — service IDs identify API service permissions, while function IDs identify specific vehicle features.
- A permissive default (create all entities) is safer than a restrictive default (create no entities) when capability data is unavailable, ensuring backward compatibility.
- Vehicle ability and plant number data are similarly static and safe to cache for the lifetime of a Home Assistant session.

## Requirements *(mandatory)*

### Functional Requirements

#### Capability Data Parsing

- **FR-001**: System MUST parse the full capability response from the vehicle capability API, extracting `functionId` and `valueEnable` for each capability object.
- **FR-002**: System MUST store capability flags as a mapping of function ID strings to boolean enabled/disabled values.
- **FR-003**: System MUST continue to extract `serviceId` values from the capability response for backward compatibility with existing service-ID-based checks.
- **FR-004**: System MUST handle malformed or incomplete capability objects gracefully, skipping individual entries that lack required fields and logging a debug-level warning.

#### Capability-to-Entity Mapping

- **FR-005**: System MUST define a mapping between capability function IDs and entity descriptions, specifying which capability flag(s) gate each entity.
- **FR-006**: System MUST support entities that require a single capability flag to be enabled.
- **FR-007**: System MUST support entities that have no capability requirement (always created regardless of capability flags).
- **FR-008**: The capability mapping MUST cover at minimum these feature categories: door lock/unlock, climate control, window control, trunk open, horn/flash, seat heating, seat ventilation, fridge, and charging.
- **FR-009**: System MUST map the following APK function IDs to their corresponding entity types:
  - `remote_control_lock` / `remote_control_unlock` → door lock entity
  - `remote_air_condition_switch` → climate entity
  - `remote_window_close` / `remote_window_open` → window control entities
  - `remote_trunk_open` → trunk button entity
  - `honk_flash` → horn/flash button entity
  - `remote_seat_preheat_switch` → seat heating entities
  - `vehicle_fridge` → fridge entities
  - `charging_status` → charging-related sensor entities

#### Entity Filtering

- **FR-010**: System MUST check capability flags before creating each entity during platform setup.
- **FR-011**: System MUST skip entity creation when the associated capability flag exists and is set to disabled (`valueEnable` is `false`).
- **FR-012**: System MUST create the entity when the associated capability flag is set to enabled (`valueEnable` is `true`).
- **FR-013**: System MUST create the entity when no capability mapping is defined for that entity type (opt-in filtering — unmapped entities default to always created).
- **FR-014**: System MUST create all entities (permissive fallback) when the capability API call fails or returns no data, to maintain backward compatibility.
- **FR-015**: System MUST log at info level the total count of entities filtered out by capability checks during setup, per entity platform.
- **FR-016**: System MUST log at debug level each individual entity that is skipped due to a disabled capability flag, including the entity key and function ID.

#### Static Data Caching

- **FR-017**: System MUST fetch capability data only once during initial coordinator setup, not on every polling cycle.
- **FR-018**: System MUST fetch vehicle ability (visual configuration) data only once during initial coordinator setup.
- **FR-019**: System MUST fetch plant number data only once during initial coordinator setup.
- **FR-020**: System MUST serve cached capability, vehicle ability, and plant number data for all subsequent data updates within the same Home Assistant session.
- **FR-021**: System MUST re-fetch all cached static data when Home Assistant restarts or the integration is reloaded.
- **FR-022**: System MUST NOT block or delay coordinator polling if static data fetching fails — failures should be logged and the coordinator should continue with available data.

#### API Documentation Updates

- **FR-023**: The capabilities endpoint documentation MUST include the full response schema showing all fields of a capability object (`functionId`, `valueEnable`, `functionCategory`, `name`, `showType`, `tips`, `valueEnum`, `valueRange`, `paramsJson`, `configCode`, `platform`, `priority`).
- **FR-024**: The entity documentation MUST include a reference table mapping entity types to their required capability function IDs.
- **FR-025**: The models documentation MUST reflect the updated capability data model with function-ID-based capability flags.

### Key Entities

- **Capability Flag**: Represents a single vehicle feature capability. Key attributes: function ID (unique string identifier, e.g., `remote_control_lock`), enabled status (boolean), function category (grouping), and optional parameters. Sourced from the vehicle capability API.
- **Capability Map Entry**: Represents the association between a capability function ID and one or more entity descriptions. Defines which capability flag(s) must be enabled for a given entity to be created. Maintained as a static configuration within the integration.
- **Vehicle Capabilities (enhanced)**: The collection of all capability flags for a specific vehicle. Key attributes: function ID to enabled-status mapping (dictionary), plus the existing service ID list for backward compatibility. Cached after initial fetch.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Vehicles missing specific features (e.g., fridge, sunroof) show zero phantom entities for those features — 100% of unsupported feature entities are filtered out.
- **SC-002**: Vehicles with all features enabled show identical entity counts and behavior compared to the current integration (zero regression in entity creation or functionality).
- **SC-003**: After initial setup, the number of API calls per polling cycle is reduced by eliminating repeated calls to the capability, vehicle ability, and plant number endpoints (3 fewer API calls per poll cycle per vehicle).
- **SC-004**: New entities added to the integration without a capability mapping are created unconditionally, ensuring the filtering system does not block future development.
- **SC-005**: Contributors can determine the required capability flag for any entity by consulting the API documentation within 2 minutes, without needing to inspect APK source code.
