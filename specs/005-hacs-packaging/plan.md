# Implementation Plan: HACS Packaging

**Branch**: `005-hacs-packaging` | **Date**: 2026-03-09 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/005-hacs-packaging/spec.md`

## Summary

Make the Hello Smart Home Assistant integration installable via HACS by adding the required metadata files (`hacs.json`, `LICENSE`), updating `manifest.json` with correct ownership and documentation fields, adding CI validation workflows for HACS and hassfest, and creating the first GitHub release to enable version tracking and update notifications.

## Technical Context

**Language/Version**: N/A — no production Python code changes; only JSON, YAML, and text files  
**Primary Dependencies**: HACS validation action (`hacs/action`), hassfest action (`home-assistant/actions/hassfest`), GitHub Actions  
**Storage**: N/A  
**Testing**: CI-based validation only (HACS action + hassfest action); no pytest changes  
**Target Platform**: GitHub repository (consumed by HACS running on Home Assistant OS/Container/Supervised)  
**Project Type**: Home Assistant custom integration (existing — packaging only)  
**Performance Goals**: N/A — no runtime code changes  
**Constraints**: Must conform to HACS repository requirements and Home Assistant manifest schema  
**Scale/Scope**: 4 new files, 1 file edit, 1 GitHub release

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Home Assistant Compatibility | ✅ PASS | No production code changes. `manifest.json` edits only fix metadata fields (`codeowners`, `documentation`). No dependency changes. |
| II. Security-First | ✅ PASS | No credentials, API calls, or user input handling. LICENSE file is non-sensitive. CI workflows run in GitHub-hosted runners with no secrets required. |
| III. Minimal Production Footprint | ✅ PASS | `hacs.json` lives at repo root (not in `custom_components/`). CI workflows live in `.github/workflows/`. No new files are added to the shipped integration. Only `manifest.json` is touched in `custom_components/`. |
| IV. Organized Testing & Reuse | ✅ PASS | CI workflows go in `.github/workflows/` per convention. No test files added. |
| V. Simplicity & Code Quality | ✅ PASS | Minimal changes — each file has a single, clear purpose. No abstractions, no speculative code. |

**Gate result**: ✅ ALL PASS — no violations, proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/005-hacs-packaging/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
./                              # Repository root
├── hacs.json                   # NEW — HACS store configuration
├── LICENSE                     # NEW — MIT license file
├── .github/
│   └── workflows/
│       └── validate.yml        # NEW — HACS + hassfest CI workflow
└── custom_components/
    └── hello_smart/
        └── manifest.json       # EDIT — fix codeowners + documentation URL
```

**Structure Decision**: No new directories needed. `hacs.json` and `LICENSE` are placed at the repo root per HACS requirements. The CI workflow goes in `.github/workflows/` per GitHub Actions convention. The only edit to existing code is `manifest.json` metadata fields.

## Complexity Tracking

> No constitution violations — this section is intentionally empty.
