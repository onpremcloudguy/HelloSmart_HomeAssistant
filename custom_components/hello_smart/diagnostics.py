"""Diagnostics support for the Hello Smart integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, SENSITIVE_FIELDS

TO_REDACT = set(SENSITIVE_FIELDS)


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Build coordinator data summary
    coordinator_data: dict[str, Any] = {}
    if coordinator.data:
        for vin, vehicle_data in coordinator.data.items():
            coordinator_data[vin] = {
                "vehicle": {
                    "vin": vehicle_data.vehicle.vin,
                    "model_name": vehicle_data.vehicle.model_name,
                    "model_year": vehicle_data.vehicle.model_year,
                    "series_code": vehicle_data.vehicle.series_code,
                },
                "status": {
                    "battery_level": vehicle_data.status.battery_level,
                    "range_remaining": vehicle_data.status.range_remaining,
                    "charging_state": vehicle_data.status.charging_state.value,
                    "charger_connected": vehicle_data.status.charger_connected,
                    "charge_voltage": vehicle_data.status.charge_voltage,
                    "charge_current": vehicle_data.status.charge_current,
                    "time_to_full": vehicle_data.status.time_to_full,
                    "doors": vehicle_data.status.doors,
                    "windows": vehicle_data.status.windows,
                    "climate_active": vehicle_data.status.climate_active,
                    "latitude": vehicle_data.status.latitude,
                    "longitude": vehicle_data.status.longitude,
                },
                "ota": {
                    "current_version": vehicle_data.ota.current_version,
                    "target_version": vehicle_data.ota.target_version,
                    "update_available": vehicle_data.ota.update_available,
                },
            }

    # Account state (without secrets)
    account_state: dict[str, Any] = {}
    if coordinator.account:
        account_state = {
            "region": coordinator.account.region.value,
            "state": coordinator.account.state.value,
            "username": coordinator.account.username,
        }

    return async_redact_data(
        {
            "config_entry_data": dict(entry.data),
            "config_entry_options": dict(entry.options),
            "coordinator_data": coordinator_data,
            "account_state": account_state,
        },
        TO_REDACT,
    )
