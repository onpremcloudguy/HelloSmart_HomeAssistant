# SmartBrandIntegration Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-07

## Active Technologies
- HA `config_entry` for credentials/settings; no new storage needed (002-apk-get-endpoints)

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
- 002-apk-get-endpoints: Added Python 3.13+ (matching Home Assistant Core 2025.x minimum) + `aiohttp` (via HA's `async_get_clientsession`), `homeassistant` core APIs (config_flow, DataUpdateCoordinator, entity platforms, device registry, diagnostics)

- 001-hello-smart-foundation: Added Python 3.13+ (matching Home Assistant Core 2025.x minimum) + `aiohttp` (via HA's `async_get_clientsession`), `homeassistant` core APIs (config_flow, DataUpdateCoordinator, entity platforms, device registry, diagnostics)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
