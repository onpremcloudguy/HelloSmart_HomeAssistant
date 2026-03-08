# Quickstart: HACS Packaging

**Feature Branch**: `005-hacs-packaging`  
**Date**: 2026-03-09

## Overview

This feature adds the metadata files and CI workflows required to make the Hello Smart integration installable via HACS. No production Python code changes are needed — only static configuration files are added or updated.

## Files to Create

### 1. `hacs.json` (repository root)

```json
{
  "name": "Hello Smart",
  "homeassistant": "2024.1.0"
}
```

### 2. `LICENSE` (repository root)

MIT license with copyright holder `onpremcloudguy` and current year.

### 3. `.github/workflows/validate.yml`

```yaml
name: Validate

on:
  push:
  pull_request:
  schedule:
    - cron: "0 0 * * 0"
  workflow_dispatch:

permissions: {}

jobs:
  validate-hacs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hacs/action@main
        with:
          category: integration
          ignore: brands

  validate-hassfest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: home-assistant/actions/hassfest@master
```

## Files to Update

### 4. `custom_components/hello_smart/manifest.json`

Change `codeowners` from `[]` to `["@onpremcloudguy"]`, update `documentation` from `"https://github.com/"` to `"https://github.com/onpremcloudguy/HelloSmart_HomeAssistant"`, and add `issue_tracker`.

## Post-Implementation Steps

### 5. Create GitHub Release

```bash
git tag 0.3.0
git push origin 0.3.0
```

Then create a full GitHub Release from the tag via the GitHub UI or CLI:

```bash
gh release create 0.3.0 --title "v0.3.0" --notes "Initial HACS release"
```

### 6. Repository Settings (manual, one-time)

- Ensure the repository is **public**
- Add a **description** to the repository
- Add **topics** (e.g., `home-assistant`, `hacs`, `smart`, `ev`, `custom-integration`)
- Ensure **Issues** are enabled

### 7. Optional: HACS Default Submission

After all checks pass, submit a PR to `hacs/default` to add `onpremcloudguy/HelloSmart_HomeAssistant` to the `integration` list. Prerequisites:
- All CI checks passing (including brand icon check)
- At least one GitHub Release
- Repository has description, topics, and issues enabled

## Verification

1. Run the HACS validation locally:
   ```bash
   # Push to GitHub and check Actions tab for validate workflow results
   ```

2. Test HACS install flow:
   - Open HACS in Home Assistant
   - Go to Integrations → three-dot menu → Custom repositories
   - Add `https://github.com/onpremcloudguy/HelloSmart_HomeAssistant` as category "Integration"
   - Search for "Hello Smart" and verify it appears with correct metadata
   - Install and restart HA
   - Confirm "Hello Smart" appears in Add Integration
