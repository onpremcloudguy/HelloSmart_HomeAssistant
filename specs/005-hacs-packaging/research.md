# Research: HACS Packaging

**Feature Branch**: `005-hacs-packaging`  
**Date**: 2026-03-09

## R1: HACS Repository Requirements

**Decision**: Use minimal `hacs.json` with `name` and `homeassistant` fields only. No `zip_release`, `content_in_root`, or other optional fields needed.

**Rationale**: The integration uses the standard `custom_components/DOMAIN/` directory layout, which is the HACS default. `zip_release` is only needed for archived bundles. `content_in_root` defaults to `false`, which is correct for integrations. Only `name` is required; `homeassistant` is recommended to prevent installs on incompatible versions.

**Alternatives considered**:
- Including `render_readme: true` — this is not a valid HACS field per the current schema; HACS always renders the README for integrations
- Including `hacs` field for minimum HACS version — not needed unless using HACS-specific features

**Concrete hacs.json**:
```json
{
  "name": "Hello Smart",
  "homeassistant": "2024.1.0"
}
```

## R2: manifest.json Required Fields

**Decision**: Add `codeowners`, fix `documentation` URL, and add `issue_tracker` field. Keep existing fields (`domain`, `name`, `version`, `config_flow`, `iot_class`, `requirements`).

**Rationale**: Hassfest validates the presence and format of required fields. The current manifest is missing a valid `codeowners` (empty array) and has a placeholder `documentation` URL. Adding `issue_tracker` is recommended for hassfest and required for HACS default submission.

**Alternatives considered**:
- Adding `integration_type: "hub"` — recommended but not strictly required for custom integrations; would improve hassfest compliance
- Adding `dependencies` — not needed unless the integration depends on other HA integrations at setup time

**Concrete manifest.json**:
```json
{
  "domain": "hello_smart",
  "name": "Hello Smart",
  "codeowners": ["@onpremcloudguy"],
  "config_flow": true,
  "documentation": "https://github.com/onpremcloudguy/HelloSmart_HomeAssistant",
  "issue_tracker": "https://github.com/onpremcloudguy/HelloSmart_HomeAssistant/issues",
  "iot_class": "cloud_polling",
  "requirements": [],
  "version": "0.3.0"
}
```

## R3: Version Tag Format

**Decision**: Use plain semver without "v" prefix (e.g., `0.3.0`, not `v0.3.0`).

**Rationale**: HACS uses the AwesomeVersion library which strips "v" prefixes automatically, but plain semver avoids ambiguity and is the recommended format. The version in the GitHub release tag should match `manifest.json`'s `version` field exactly.

**Alternatives considered**:
- Using `v0.3.0` with "v" prefix — works but adds unnecessary inconsistency between manifest.json and the tag name
- Using CalVer (e.g., `2026.3.0`) — valid but would require changing the existing versioning scheme

## R4: CI Validation Workflow

**Decision**: Single workflow file (`validate.yml`) with two jobs: HACS validation and hassfest. Trigger on push, pull_request, weekly schedule, and manual dispatch.

**Rationale**: Combining both checks in one workflow reduces file count. Running on push and PR catches issues early. Weekly schedule detects drift if upstream tools change validation rules. The `hacs/action@main` and `home-assistant/actions/hassfest@master` are the officially recommended action references.

**Alternatives considered**:
- Separate workflow files per check — adds file count for no benefit
- Running only on PR — misses issues pushed directly to the default branch
- Pinning action versions — `hacs/action` only offers `main` branch (no versioned tags)

**Key detail**: Use `ignore: "brands"` in the HACS action to skip brand icon validation initially, since the `brand/icon.png` can be added later or submitted to the home-assistant/brands repo separately.

## R5: License File

**Decision**: MIT license.

**Rationale**: MIT is the most common license among Home Assistant custom integrations. It is permissive, well-understood, and compatible with the Home Assistant project (Apache-2.0). HACS requires a license file to be present at the repo root.

**Alternatives considered**:
- Apache-2.0 — matches Home Assistant Core's license but is more complex for a small project
- GPL-3.0 — more restrictive than necessary for a custom integration

## R6: HACS Default Submission Prerequisites

**Decision**: Document the prerequisites but do not submit automatically. The maintainer should submit manually after verifying all checks pass.

**Rationale**: Default submission requires human verification (must be the repo owner), a real GitHub release, public repo with description/topics/issues enabled, and a brand icon. Some of these are one-time manual steps.

**Prerequisites identified**:
1. Repository must be public
2. GitHub description, topics, and issues must be enabled
3. At least one full GitHub Release (not just a tag)
4. `hacs/action` passes with no ignored checks (except `brands` initially)
5. `hassfest` passes
6. Brand icon (`brand/icon.png`) must exist — or submit to `home-assistant/brands` repo
7. Submitter must be the repo owner or major contributor

## R7: Brand Icon

**Decision**: Create a minimal `brand/` directory with icon.png for HACS default submission readiness, or defer to a separate task.

**Rationale**: The HACS default submission checks for brand assets. For custom repository usage this is not required. The `ignore: "brands"` flag in the CI workflow allows skipping this check initially. A proper brand icon can be designed and added later.

**Alternatives considered**:
- Submitting to `home-assistant/brands` repo — this is the proper long-term approach but is a separate workflow with its own review process
- Skipping entirely — works for custom repo usage but blocks default submission
