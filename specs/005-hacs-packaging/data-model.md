# Data Model: HACS Packaging

**Feature Branch**: `005-hacs-packaging`  
**Date**: 2026-03-09

## Entities

This feature introduces no runtime data entities. All artifacts are static configuration files consumed by external tools (HACS, hassfest, GitHub Actions). The "data model" here describes the schema and validation rules for each file.

### hacs.json

| Field | Type | Required | Validation Rule |
|-------|------|----------|----------------|
| `name` | string | Yes | Non-empty string; displayed in HACS UI |
| `homeassistant` | string | No | Valid AwesomeVersion string (SemVer or CalVer) |

**Relationships**: Referenced by HACS during repository discovery and installation. Must exist at repository root.

**State transitions**: N/A — static file, no state changes.

### manifest.json (updated fields)

| Field | Type | Required | Validation Rule |
|-------|------|----------|----------------|
| `domain` | string | Yes | Alphanumeric + underscore; must match directory name |
| `name` | string | Yes | Non-empty display name |
| `version` | string | Yes | Valid SemVer or CalVer (AwesomeVersion) |
| `codeowners` | array[string] | Yes | Each entry: `"@github_username"` format |
| `documentation` | string | Yes | Valid URL format (not validated for reachability) |
| `issue_tracker` | string | Yes | Valid URL format pointing to GitHub issues |
| `config_flow` | boolean | Yes | Must be `true` for UI-configured integrations |
| `iot_class` | string | Yes | One of: `local_polling`, `local_push`, `cloud_polling`, `cloud_push`, `assumed_state`, `calculated` |
| `requirements` | array[string] | No | PyPI package specifiers |

**Relationships**: Consumed by Home Assistant at integration load time and by hassfest for validation. `version` must match GitHub release tag.

### CI Workflow (validate.yml)

| Field | Type | Description |
|-------|------|-------------|
| `on.push` | trigger | Runs on all pushes |
| `on.pull_request` | trigger | Runs on all PRs |
| `on.schedule` | trigger | Weekly cron for drift detection |
| `on.workflow_dispatch` | trigger | Manual trigger |
| `jobs.validate-hacs` | job | Runs `hacs/action@main` with `category: integration` |
| `jobs.validate-hassfest` | job | Runs `home-assistant/actions/hassfest@master` |

**Relationships**: Consumes both `hacs.json` and `manifest.json`. Reports pass/fail on GitHub PRs.

### GitHub Release

| Field | Type | Validation Rule |
|-------|------|----------------|
| `tag_name` | string | Plain semver (e.g., `0.3.0`), must match `manifest.json` version |
| `name` | string | Human-readable release title |
| `body` | string | Release notes / changelog |
| `prerelease` | boolean | Set `true` for beta versions (tag contains `b`) |

**Relationships**: HACS reads the latest release tag to determine available version. Tag must match `manifest.json`'s `version` field for consistency.

### LICENSE

No schema — plain text file. Must exist at repository root. Content is the full MIT license text with correct copyright year and holder name.
