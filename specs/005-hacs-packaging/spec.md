# Feature Specification: HACS Packaging

**Feature Branch**: `005-hacs-packaging`  
**Created**: 2026-03-09  
**Status**: Draft  
**Input**: User description: "Make the Hello Smart integration installable via HACS (Home Assistant Community Store). The integration already lives under custom_components/hello_smart/ with a working manifest.json, config_flow, and all platform files. The repository is hosted on GitHub but is currently missing the files and metadata HACS requires."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install Integration via HACS Custom Repository (Priority: P1)

A Home Assistant user wants to install the Hello Smart integration without manually copying files. They add the GitHub repository URL as a custom repository in HACS, search for "Hello Smart", and install it. After restarting Home Assistant, the integration appears in Settings → Devices & Services → Add Integration.

**Why this priority**: This is the core value proposition — without a working HACS install flow, none of the other stories matter. It removes the manual file-copy barrier that discourages adoption.

**Independent Test**: Can be fully tested by adding the repository as a custom HACS repository, installing it, restarting HA, and confirming the integration appears in the Add Integration dialog.

**Acceptance Scenarios**:

1. **Given** a Home Assistant instance with HACS installed, **When** the user adds the repository URL as a custom repository (category: Integration), **Then** "Hello Smart" appears in the HACS integration list with its name, description, and version.
2. **Given** the user has added the custom repository, **When** they click Install, **Then** the `custom_components/hello_smart/` directory is correctly deployed to their HA config directory.
3. **Given** the installation is complete and HA has been restarted, **When** the user navigates to Add Integration, **Then** "Hello Smart" appears and the config flow starts normally.

---

### User Story 2 - Receive Update Notifications (Priority: P2)

A user who has already installed Hello Smart via HACS wants to know when a new version is available. When the maintainer publishes a new GitHub release with a version tag, HACS detects the update and notifies the user. The user can then update in-place without manual intervention.

**Why this priority**: Update notifications are what make HACS valuable over a manual install. Without them, users have no way to know when fixes or features are available.

**Independent Test**: Can be tested by publishing a new GitHub release with a bumped version tag and confirming HACS shows an update available for the integration.

**Acceptance Scenarios**:

1. **Given** a user has Hello Smart installed via HACS at version 0.3.0, **When** the maintainer publishes a new GitHub release tagged 0.4.0, **Then** HACS shows an update notification for Hello Smart.
2. **Given** an update is available, **When** the user clicks Update in HACS, **Then** the integration files are replaced with the new version and the user is prompted to restart HA.

---

### User Story 3 - CI Validates HACS Compliance (Priority: P3)

A contributor or maintainer pushes code changes or opens a pull request. Automated CI checks run to verify that the repository structure, manifest, and HACS configuration remain valid. This prevents accidental breakage of the HACS install flow.

**Why this priority**: CI validation prevents regressions. Without it, a small change to manifest.json or a missing field could silently break HACS installs for all users.

**Independent Test**: Can be tested by pushing a commit to the repository and confirming the CI workflow runs and reports pass/fail status on the pull request.

**Acceptance Scenarios**:

1. **Given** a pull request is opened, **When** CI runs, **Then** the HACS validation check passes if the repository structure and metadata are correct.
2. **Given** a pull request is opened, **When** CI runs, **Then** the Home Assistant manifest validation (hassfest) check passes if manifest.json contains all required fields with valid values.
3. **Given** a contributor removes a required field from manifest.json, **When** they push the change, **Then** CI fails and clearly indicates which validation failed.

---

### User Story 4 - Submit to HACS Default Repository List (Priority: P4)

The maintainer wants Hello Smart to be discoverable in HACS without users needing to add a custom repository URL. They submit the repository to the HACS default repository list. The repository must meet all HACS requirements: public repo, valid hacs.json, valid manifest.json, a license file, at least one GitHub release, and a populated README.

**Why this priority**: Default listing increases discoverability but is not required for the install flow to work. It is a nice-to-have after the custom-repository flow is solid.

**Independent Test**: Can be tested by running the HACS validation action locally and confirming all checks pass, then verifying the repository meets all published HACS default repository submission criteria.

**Acceptance Scenarios**:

1. **Given** all required files and metadata are in place, **When** the HACS validation action runs against the repository, **Then** all checks pass with no errors.
2. **Given** the repository is public, has a license, a release, and valid metadata, **When** the maintainer submits a PR to the HACS default repository, **Then** the submission meets all published acceptance criteria.

---

### Edge Cases

- What happens if the user installs via HACS but the repository has no GitHub releases yet? HACS may show the integration but fail to install or show version "0.0.0". The repository must have at least one tagged release before advertising HACS support.
- What happens if the version in manifest.json does not match the GitHub release tag? HACS uses the GitHub release tag as the version. A mismatch could confuse users about which version they have. The release process must enforce that these stay in sync.
- What happens if codeowners in manifest.json contains a GitHub handle that does not exist? Hassfest validation will fail. The handle must be a valid GitHub username prefixed with `@`.
- What happens if a user has previously installed the integration manually and then installs via HACS? HACS will overwrite the files in custom_components/hello_smart/. The user's configuration (config entries) will be preserved since those live in HA's database, not in the integration directory.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Repository MUST contain a valid `hacs.json` file at the root with the integration name and minimum Home Assistant version
- **FR-002**: Repository MUST contain a `LICENSE` file at the root
- **FR-003**: The `manifest.json` MUST have a populated `codeowners` field with at least one valid GitHub handle
- **FR-004**: The `manifest.json` MUST have a valid `documentation` URL pointing to the actual repository
- **FR-005**: The `manifest.json` MUST contain all required fields: `domain`, `name`, `version`, `codeowners`, `documentation`, `config_flow`, `iot_class`
- **FR-006**: The `custom_components/` directory MUST remain at the repository root (not nested in subdirectories)
- **FR-007**: Repository MUST have at least one GitHub release with a semantic version tag (e.g., `v0.3.0` or `0.3.0`) that matches the version in `manifest.json`
- **FR-008**: Repository MUST include a CI workflow that runs HACS validation on pushes and pull requests
- **FR-009**: Repository MUST include a CI workflow that runs Home Assistant manifest validation (hassfest) on pushes and pull requests
- **FR-010**: The README MUST include installation instructions for both HACS custom repository and manual installation methods

### Key Entities

- **hacs.json**: HACS store configuration file — defines integration name, README rendering preference, and minimum Home Assistant version requirement
- **manifest.json**: Home Assistant integration manifest — defines the integration identity, ownership, documentation link, and compatibility metadata
- **LICENSE**: Open-source license file — required by HACS for any listed integration; defines the terms under which the code may be used and distributed
- **CI Workflow**: Automated validation pipeline — runs HACS and hassfest checks on code changes to prevent regressions in HACS compatibility
- **GitHub Release**: Versioned distribution artifact — used by HACS to detect available versions and deliver updates to users

## Assumptions

- The repository is hosted at `https://github.com/onpremcloudguy/HelloSmart_HomeAssistant` and will be made public (or is already public)
- The maintainer's GitHub handle is `@onpremcloudguy` (derived from the repository URL)
- MIT is an appropriate license for this project (standard choice for Home Assistant community integrations)
- The minimum supported Home Assistant version is 2024.1.0 (a reasonable baseline for current integrations)
- The existing `custom_components/hello_smart/` directory structure and file layout already conforms to Home Assistant integration standards (confirmed by working config_flow and platform files)
- Version tags will use the format `vX.Y.Z` (e.g., `v0.3.0`) to match common HACS conventions
- The README already contains adequate installation instructions (confirmed: HACS and Manual sections exist)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can add the repository as a HACS custom repository and install "Hello Smart" in under 5 minutes, with no manual file operations
- **SC-002**: HACS displays the correct integration name, version, and description after adding the custom repository
- **SC-003**: When a new GitHub release is published, HACS detects the update and shows an update notification within its normal refresh cycle
- **SC-004**: The HACS validation CI check passes with zero errors on the default branch
- **SC-005**: The hassfest CI check passes with zero errors on the default branch
- **SC-006**: The repository meets 100% of the HACS default repository submission criteria as documented in the HACS contribution guidelines
