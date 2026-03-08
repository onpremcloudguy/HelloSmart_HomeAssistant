# Contract: HACS Repository Metadata

**Feature**: 005-hacs-packaging  
**Type**: Configuration schema — consumed by external tools (HACS, hassfest, GitHub Actions)

## hacs.json Contract

**Location**: Repository root (`./hacs.json`)  
**Consumed by**: HACS (during add-custom-repository and update-check flows)

```json
{
  "name": "Hello Smart",
  "homeassistant": "2024.1.0"
}
```

### Validation Rules
- File must be valid JSON
- `name` must be a non-empty string
- `homeassistant` must be a valid version string parseable by AwesomeVersion

---

## manifest.json Contract

**Location**: `custom_components/hello_smart/manifest.json`  
**Consumed by**: Home Assistant (integration loading), hassfest (CI validation), HACS (metadata display)

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

### Validation Rules
- `domain` must equal the parent directory name under `custom_components/`
- `codeowners` must be a non-empty array of strings in `"@username"` format
- `documentation` must be a valid URL string
- `issue_tracker` must be a valid URL string
- `version` must be valid SemVer or CalVer

---

## GitHub Release Contract

**Consumed by**: HACS (version detection and update notifications)

| Property | Requirement |
|----------|-------------|
| Tag name | Plain semver (e.g., `0.3.0`), no `v` prefix |
| Tag ↔ manifest.json | Tag must match `version` field in manifest.json |
| Release type | Must be a full GitHub Release (not just a tag) |
| Pre-release flag | Set `true` if tag contains `b` (e.g., `0.4.0b1`) |

---

## CI Workflow Contract

**Location**: `.github/workflows/validate.yml`  
**Consumed by**: GitHub Actions (triggered on push/PR/schedule/manual)

### Jobs

| Job | Action | Input | Pass condition |
|-----|--------|-------|----------------|
| `validate-hacs` | `hacs/action@main` | `category: integration` | hacs.json valid, repo structure valid |
| `validate-hassfest` | `home-assistant/actions/hassfest@master` | (none) | manifest.json all required fields valid |
