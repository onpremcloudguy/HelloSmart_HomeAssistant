<!--
  Sync Impact Report
  ──────────────────
  Version change: 0.0.0 → 1.0.0 (MAJOR — initial ratification)
  Modified principles: N/A (initial version)
  Added sections:
    - Core Principles (5 principles)
    - Technology Constraints
    - Development Workflow
    - Governance
  Removed sections: N/A
  Templates requiring updates:
    - .specify/templates/plan-template.md — ✅ compatible (no changes needed)
    - .specify/templates/spec-template.md — ✅ compatible (no changes needed)
    - .specify/templates/tasks-template.md — ✅ compatible (no changes needed)
  Follow-up TODOs: None
-->

# SmartBrandIntegration Constitution

## Core Principles

### I. Home Assistant Compatibility (NON-NEGOTIABLE)

All code MUST use Python versions and libraries supported by the
target Home Assistant release. No third-party packages outside the
Home Assistant runtime dependency tree are permitted in production
code unless explicitly approved.

- Python version MUST match the Home Assistant Core minimum
  (currently Python 3.13 for HA 2025.x).
- All async code MUST use `asyncio` patterns consistent with the
  HA event loop; blocking I/O in the event loop is forbidden.
- Dependencies MUST be declared in `manifest.json` and MUST be
  packages already available in the HA package index or PyPI with
  compatible licensing.

**Rationale**: Home Assistant runs inside a managed Python
environment. Incompatible versions or unsanctioned dependencies
cause runtime failures and block HACS/core review.

### II. Security-First (NON-NEGOTIABLE)

All code MUST adhere to security best practices aligned with the
OWASP Top 10 and Home Assistant security guidelines.

- Credentials, API keys, and tokens MUST NEVER be hardcoded; they
  MUST be stored via HA's `config_entry` secrets or the HA secrets
  vault (`secrets.yaml`).
- All external HTTP calls MUST use TLS (HTTPS) and MUST validate
  certificates. Plain HTTP is forbidden for production endpoints.
- User-supplied and external data MUST be validated and sanitized
  before use. No raw string interpolation into URLs, commands, or
  queries.
- OAuth flows MUST use the HA built-in OAuth2 implementation where
  available.
- Sensitive data MUST NEVER appear in logs. Use `async_redact_data`
  or equivalent redaction before logging.
- SSRF vectors MUST be mitigated: external URLs MUST be validated
  against an allowlist or constrained to known API base URLs.

**Rationale**: The integration runs on the user's home network with
access to local devices. A security flaw can expose the entire
smart-home environment.

### III. Minimal Production Footprint

Only the minimal, high-quality code required for runtime operation
MUST be included in the Home Assistant server installation. Every
file shipped in the integration package MUST justify its presence.

- No test utilities, debug scripts, mock data, or development-only
  dependencies in the `custom_components/` production directory.
- No unused imports, dead code paths, or commented-out blocks in
  production files.
- Configuration options MUST default to safe, sensible values so
  the integration works with minimal user setup.
- Code MUST follow the Home Assistant integration quality scale
  guidelines (Silver tier or above as a target).

**Rationale**: Home Assistant integrations are loaded into a shared
Python process. Unnecessary code increases memory footprint, attack
surface, and maintenance burden.

### IV. Organized Testing & Reuse

Test and debug scripts MUST be stored in designated directories and
reused across features to reduce file sprawl.

- All tests MUST reside under a top-level `tests/` directory,
  mirroring the production source structure.
- Shared test fixtures and helpers MUST be placed in
  `tests/conftest.py` or `tests/helpers/` and imported rather than
  duplicated.
- Debug and diagnostic scripts MUST reside under `scripts/debug/`
  (never in `custom_components/`).
- Reusable development utilities (linting configs, CI helpers) MUST
  reside under `scripts/` at the repository root.
- A new test file is permitted only when no existing file covers
  the same component or entity scope.

**Rationale**: Uncontrolled file sprawl makes navigation difficult,
increases merge conflicts, and hides redundant test logic.

### V. Simplicity & Code Quality

Every line of code MUST justify its presence. Follow YAGNI (You
Aren't Gonna Need It) rigorously.

- No speculative abstractions, wrapper layers, or factory patterns
  unless demonstrably required by the current feature set.
- Prefer Home Assistant's built-in helpers (`coordinator`,
  `entity`, `config_flow`) over custom implementations.
- Code MUST pass `ruff` linting and formatting checks with the
  project's configured ruleset.
- Functions MUST have a single clear responsibility; if a function
  exceeds ~40 lines, evaluate decomposition.
- MUST NOT add type annotations, docstrings, or comments to code
  that was not changed unless the existing code is actively
  misleading.

**Rationale**: Complexity is the primary source of bugs in
long-lived integrations. Minimal code is easier to audit, review,
and maintain.

## Technology Constraints

- **Language**: Python (version matching Home Assistant Core
  requirements — currently 3.13+).
- **Async framework**: `asyncio` via Home Assistant's event loop.
  No threads unless wrapped with
  `hass.async_add_executor_job()`.
- **HTTP client**: `aiohttp` (HA's bundled client). Do not
  introduce `requests` or `httpx` in production code.
- **Configuration**: HA config flows (`config_flow.py`) for user
  setup; `const.py` for integration constants.
- **Data coordination**: `DataUpdateCoordinator` for polling-based
  data refresh.
- **Storage**: HA `Store` helper for persistent local data; no
  direct filesystem writes outside HA's storage directory.
- **Logging**: Python `logging` module via
  `logging.getLogger(__name__)`. No print statements.

## Development Workflow

- **Branch strategy**: Feature branches off `main`; one feature per
  branch.
- **Directory layout**:
  - `custom_components/smart_brand_integration/` — production code
    (shipped to HA).
  - `tests/` — all test code (unit, integration, contract).
  - `scripts/` — development and debug utilities.
  - `docs/` — project documentation.
  - `.specify/` — SpecKit artifacts (specs, plans, tasks).
- **Quality gates before merge**:
  1. All tests pass (`pytest`).
  2. `ruff check` and `ruff format --check` pass.
  3. No new security warnings from static analysis.
  4. Constitution compliance verified (this document).
- **Code review**: Every PR MUST be reviewed against the
  constitution principles before merge.

## Governance

This constitution is the authoritative source of project standards
for SmartBrandIntegration. It supersedes all other guidance when
conflicts arise.

- **Amendments** require: (1) a written proposal describing the
  change, (2) rationale for why the current principle is
  insufficient, (3) an updated version number following SemVer.
- **Version policy**: MAJOR for principle removals or
  backward-incompatible redefinitions; MINOR for new principles or
  material expansions; PATCH for clarifications and wording fixes.
- **Compliance review**: Every PR and spec MUST include a
  constitution check confirming adherence to all five core
  principles.
- **Runtime guidance**: Refer to `docs/` for implementation
  patterns and quickstart instructions that elaborate on these
  principles.

**Version**: 1.0.0 | **Ratified**: 2026-03-07 | **Last Amended**: 2026-03-07
