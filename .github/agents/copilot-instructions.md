# SmartBrandIntegration Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-07

## Active Technologies
- HA `config_entry` for credentials/settings; no new storage needed (002-apk-get-endpoints)
- Python 3.13+ (matching Home Assistant Core 2025.x minimum) + `aiohttp` (via HA's `async_get_clientsession`), `homeassistant` core APIs (config_flow, DataUpdateCoordinator, entity platforms, device registry) (003-api-command-controls)
- YAML (Home Assistant Lovelace dashboard format) + Home Assistant 2025.x+, HACS (optional), mushroom cards (optional), card-mod (optional) (004-lovelace-dashboard)
- N/A — static YAML files and PNG image assets (004-lovelace-dashboard)
- N/A — no production Python code changes; only JSON, YAML, and text files + HACS validation action (`hacs/action`), hassfest action (`home-assistant/actions/hassfest`), GitHub Actions (005-hacs-packaging)
- Python 3.13+ (Home Assistant 2025.x minimum) + `aiohttp` (HA-bundled HTTP client), `homeassistant` core APIs (`DataUpdateCoordinator`, `Entity`, `ConfigEntry`) (006-capability-entity-filtering)
- In-memory caching on `SmartDataCoordinator` instance; no persistent storage needed (006-capability-entity-filtering)

- Python 3.13+ (matching Home Assistant Core 2025.x minimum) + `aiohttp` (via HA's `async_get_clientsession`), `homeassistant` core APIs (config_flow, DataUpdateCoordinator, entity platforms, device registry, diagnostics) (001-hello-smart-foundation)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.13+ (matching Home Assistant Core 2025.x minimum): Follow standard conventions

## Recent Changes
- 006-capability-entity-filtering: Added Python 3.13+ (Home Assistant 2025.x minimum) + `aiohttp` (HA-bundled HTTP client), `homeassistant` core APIs (`DataUpdateCoordinator`, `Entity`, `ConfigEntry`)
- 005-hacs-packaging: Added N/A — no production Python code changes; only JSON, YAML, and text files + HACS validation action (`hacs/action`), hassfest action (`home-assistant/actions/hassfest`), GitHub Actions
- 004-lovelace-dashboard: Added YAML (Home Assistant Lovelace dashboard format) + Home Assistant 2025.x+, HACS (optional), mushroom cards (optional), card-mod (optional)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
