# Contract: Entity Capability Filtering

**Type**: Internal integration pattern
**Scope**: All entity platforms (`sensor.py`, `binary_sensor.py`, `switch.py`, `lock.py`, `button.py`, `select.py`, `climate.py`, `number.py`, `time.py`)

## Pattern

Each entity description dataclass gains an optional `required_capability` field.
Entity filtering occurs **once** during `async_setup_entry()`, not per-poll.

## Entity Description Contract

Every platform's entity description dataclass MUST follow this pattern:

```python
@dataclass(frozen=True, kw_only=True)
class Smart<Platform>EntityDescription(<Platform>EntityDescription):
    # ... existing fields ...
    required_capability: str | None = None  # NEW: opt-in capability gating
```

- `required_capability = None` → entity is always created (default, backward-compatible)
- `required_capability = "some_function_id"` → entity is only created if `capability_flags.get("some_function_id", True)` is `True`

## Filtering Contract

Every platform's `async_setup_entry()` MUST apply this filtering logic:

```
for description in DESCRIPTIONS:
    1. Check required_capability:
       - If None → proceed to create
       - If set AND caps.capability_flags is non-empty:
         - If capability_flags.get(required_capability, True) is False → SKIP
         - Otherwise → proceed to create
    2. Check existing available_fn (if platform has it):
       - If returns False → SKIP
    3. Create entity
```

## Logging Contract

| Level | When | Format |
|-------|------|--------|
| DEBUG | Entity skipped due to disabled capability | `"Skipping %s for %s: capability '%s' disabled"` (entity_key, vin_prefix, function_id) |
| INFO | After all entities processed per platform | `"%s: created %d entities, filtered %d by capability for %s"` (platform, created, filtered, vin_prefix) |

## Invariants

1. A `None` `required_capability` MUST NEVER cause an entity to be filtered
2. Empty `capability_flags` dict MUST NEVER cause any entity to be filtered
3. A function ID not present in `capability_flags` MUST NOT cause filtering
4. Only an explicitly `False` value for the matching function ID causes filtering
5. The total entities created when capabilities are unavailable MUST equal the total entities created in the current integration version (zero regression)
