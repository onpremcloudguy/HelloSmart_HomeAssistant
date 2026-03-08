# Tasks: HACS Packaging

**Input**: Design documents from `/specs/005-hacs-packaging/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Not requested — no test tasks included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup

**Purpose**: Ensure repository structure is correct and existing files are in a valid state

- [x] T001 Verify custom_components/hello_smart/ directory is at repository root (not nested)

---

## Phase 2: Foundational (HACS Metadata & License)

**Purpose**: Create the core files required for any HACS installation. MUST be complete before user story validation.

**⚠️ CRITICAL**: US1 (HACS install) cannot work without these files in place.

- [x] T002 [P] Create HACS configuration file at ./hacs.json with name "Hello Smart" and homeassistant minimum "2024.1.0"
- [x] T003 [P] Create MIT license file at ./LICENSE with copyright holder and current year
- [x] T004 [P] Update custom_components/hello_smart/manifest.json: set codeowners to ["@onpremcloudguy"], set documentation to "https://github.com/onpremcloudguy/HelloSmart_HomeAssistant", add issue_tracker field "https://github.com/onpremcloudguy/HelloSmart_HomeAssistant/issues"

**Checkpoint**: All three foundational files in place — repository is structurally HACS-compatible

---

## Phase 3: User Story 1 — Install Integration via HACS Custom Repository (Priority: P1) 🎯 MVP

**Goal**: A user can add the repo as a HACS custom repository, find "Hello Smart", and install it.

**Independent Test**: Add the GitHub repo URL as a custom HACS repository (category: Integration), verify "Hello Smart" appears with correct name and version, install it, restart HA, and confirm it shows in Add Integration.

### Implementation for User Story 1

- [x] T005 [US1] Verify hacs.json is valid JSON and contains required "name" field at ./hacs.json
- [x] T006 [US1] Verify manifest.json passes schema validation: domain matches directory name, codeowners is non-empty, documentation is a valid URL, version is valid semver at custom_components/hello_smart/manifest.json
- [x] T007 [US1] Verify README.md contains HACS installation instructions (custom repository method) at ./README.md

**Checkpoint**: User Story 1 — HACS custom repository install flow is fully functional

---

## Phase 4: User Story 2 — Receive Update Notifications (Priority: P2)

**Goal**: HACS detects new GitHub releases and shows update notifications to users.

**Independent Test**: Create a GitHub release tagged `0.3.0` matching manifest.json version, then verify HACS recognizes the version. Bump manifest.json to `0.4.0` and create a new release to confirm HACS shows an update available.

### Implementation for User Story 2

- [ ] T008 [US2] Create initial GitHub release: tag `0.3.0`, title "v0.3.0 — Initial HACS Release", with release notes from CHANGELOG.md (manual step via `gh release create 0.3.0`)
  > **⚠️ MANUAL**: Run after pushing this branch to origin. Commands:
  > ```
  > git tag 0.3.0
  > git push origin 0.3.0
  > gh release create 0.3.0 --title "v0.3.0 — Initial HACS Release" --notes "Initial HACS-compatible release"
  > ```
- [x] T009 [US2] Verify manifest.json version field "0.3.0" matches the GitHub release tag "0.3.0" at custom_components/hello_smart/manifest.json

**Checkpoint**: User Story 2 — HACS can detect versions and notify users of updates

---

## Phase 5: User Story 3 — CI Validates HACS Compliance (Priority: P3)

**Goal**: Automated CI checks run on push/PR to verify HACS and hassfest compliance, preventing regressions.

**Independent Test**: Push a commit and verify the validate workflow runs. Then intentionally break manifest.json (remove a required field), push, and confirm CI fails with a clear error.

### Implementation for User Story 3

- [x] T010 [US3] Create CI validation workflow at .github/workflows/validate.yml with HACS validation job (hacs/action@main, category: integration, ignore: brands) and hassfest job (home-assistant/actions/hassfest@master), triggered on push, pull_request, weekly schedule, and workflow_dispatch
- [x] T011 [US3] Verify workflow uses minimal permissions (permissions: {}) and runs on ubuntu-latest at .github/workflows/validate.yml

**Checkpoint**: User Story 3 — CI catches HACS/manifest regressions on every push and PR

---

## Phase 6: User Story 4 — Submit to HACS Default Repository List (Priority: P4)

**Goal**: Repository meets all HACS default submission criteria so the maintainer can submit a PR to hacs/default.

**Independent Test**: Run `hacs/action` locally without `ignore` flags and confirm all checks pass. Verify repo has description, topics, issues enabled, and at least one release.

### Implementation for User Story 4

- [ ] T012 [US4] Configure GitHub repository settings: add description, add topics (home-assistant, hacs, smart, ev, custom-integration), enable Issues (manual step via GitHub UI or `gh repo edit`)
  > **⚠️ MANUAL**: Run after pushing to origin:
  > ```
  > gh repo edit --description "Home Assistant custom integration for Smart electric vehicles" --add-topic home-assistant --add-topic hacs --add-topic smart --add-topic ev --add-topic custom-integration
  > ```
- [ ] T013 [US4] Ensure repository is set to public visibility (manual step via GitHub UI or `gh repo edit --visibility public`)
  > **⚠️ MANUAL**: Run when ready: `gh repo edit --visibility public`
- [x] T014 [US4] Verify all HACS default submission prerequisites are met: public repo, LICENSE exists, at least one release, hacs.json valid, manifest.json valid, README exists, description set, topics set, issues enabled

**Checkpoint**: User Story 4 — Repository is ready for HACS default submission

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and documentation

- [ ] T015 Run quickstart.md end-to-end validation: add repo as HACS custom repository, install, restart HA, confirm integration loads
  > **⚠️ MANUAL**: Requires a running HA instance with HACS. Test after pushing to GitHub and creating the release.
- [x] T016 Update CHANGELOG.md with HACS packaging changes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — verification only
- **Foundational (Phase 2)**: Depends on Phase 1 — creates all required files
- **US1 (Phase 3)**: Depends on Phase 2 — validates HACS install readiness
- **US2 (Phase 4)**: Depends on Phase 2 — requires manifest.json to be correct for version matching
- **US3 (Phase 5)**: Depends on Phase 2 — CI validates the files created in Phase 2
- **US4 (Phase 6)**: Depends on Phases 2, 4, and 5 — needs release, CI, and all metadata
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on Foundational only — core MVP
- **User Story 2 (P2)**: Depends on Foundational only — independent of US1 validation
- **User Story 3 (P3)**: Depends on Foundational only — CI validates the same files
- **User Story 4 (P4)**: Depends on US2 (needs a release) and US3 (needs CI passing)

### Parallel Opportunities

- T002, T003, T004 can all run in parallel (different files, no dependencies)
- US1 validation (T005–T007) can start as soon as Phase 2 is complete
- US2 (T008–T009) and US3 (T010–T011) can run in parallel after Phase 2
- US4 (T012–T014) must wait for US2 and US3

---

## Parallel Example: Phase 2 (Foundational)

```
# All three can run simultaneously — different files, no dependencies:
T002: Create ./hacs.json
T003: Create ./LICENSE
T004: Update custom_components/hello_smart/manifest.json
```

## Parallel Example: User Stories 1–3 (after Phase 2)

```
# Once Phase 2 is complete, these three story phases can run in parallel:
US1 (T005–T007): Validate HACS install readiness
US2 (T008–T009): Create GitHub release
US3 (T010–T011): Create CI workflow
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup verification
2. Complete Phase 2: Create hacs.json, LICENSE, update manifest.json
3. Complete Phase 3: Validate US1 (HACS custom repo install)
4. **STOP and VALIDATE**: Test by adding as HACS custom repository
5. Deploy if ready — users can install via HACS immediately

### Incremental Delivery

1. Complete Setup + Foundational → Files in place
2. Add US1 validation → HACS custom repo install works (MVP!)
3. Add US2 → Create release → HACS shows version + update notifications
4. Add US3 → CI validation → Regressions caught automatically
5. Add US4 → Repo settings → Ready for HACS default submission
6. Each story adds value without breaking previous stories

---

## Notes

- T002, T003, T004 marked [P] — different files, no dependencies
- T008, T012, T013 are manual steps (GitHub CLI or UI) — not automatable code changes
- No test tasks included — the spec did not request tests; validation is via CI workflows and manual HACS install testing
- Commit after each phase for clean history
