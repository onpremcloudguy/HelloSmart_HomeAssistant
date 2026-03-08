"""Climate entities for the Hello Smart integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SERVICE_ID_CLIMATE
from .coordinator import SmartDataCoordinator

MIN_TEMP = 16.0
MAX_TEMP = 30.0
CLIMATE_DURATION = 180


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hello Smart climate entities from a config entry."""
    coordinator: SmartDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SmartClimate] = []
    for vin in coordinator.data:
        entities.append(SmartClimate(coordinator=coordinator, vin=vin))

    async_add_entities(entities)


class SmartClimate(CoordinatorEntity[SmartDataCoordinator], ClimateEntity):
    """Representation of Hello Smart climate pre-conditioning."""

    _attr_has_entity_name = True
    _attr_translation_key = "smart_climate"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT_COOL]
    _attr_min_temp = MIN_TEMP
    _attr_max_temp = MAX_TEMP
    _attr_target_temperature_step = 0.5

    def __init__(
        self,
        coordinator: SmartDataCoordinator,
        vin: str,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._vin = vin
        self._attr_unique_id = f"{vin}_smart_climate"
        self._attr_device_info = coordinator.get_device_info(vin)
        self._target_temp: float = 22.0
        self._optimistic_hvac_mode: HVACMode | None = None

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        if self._optimistic_hvac_mode is not None:
            return self._optimistic_hvac_mode
        data = self.coordinator.data.get(self._vin)
        if data is None:
            return HVACMode.OFF
        return HVACMode.HEAT_COOL if data.status.climate_active else HVACMode.OFF

    @property
    def target_temperature(self) -> float:
        """Return the target temperature."""
        return self._target_temp

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set the HVAC mode (start/stop climate)."""
        if hvac_mode == HVACMode.HEAT_COOL:
            await self._async_start_climate()
        else:
            await self._async_stop_climate()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set the target temperature."""
        temp = kwargs.get(ATTR_TEMPERATURE)
        if temp is None:
            return
        self._target_temp = max(MIN_TEMP, min(MAX_TEMP, float(temp)))
        # If climate is active, restart with new temp
        if self.hvac_mode == HVACMode.HEAT_COOL:
            await self._async_start_climate()
        else:
            self.async_write_ha_state()

    async def async_turn_on(self) -> None:
        """Turn on climate pre-conditioning."""
        await self._async_start_climate()

    async def async_turn_off(self) -> None:
        """Turn off climate pre-conditioning."""
        await self._async_stop_climate()

    async def _async_start_climate(self) -> None:
        """Start climate pre-conditioning at current target temperature."""
        service_parameters = [
            {"key": "rce.conditioner", "value": "1"},
            {"key": "rce.temp", "value": str(self._target_temp)},
        ]
        await self.coordinator.async_send_vehicle_command(
            self._vin,
            SERVICE_ID_CLIMATE,
            "start",
            service_parameters,
            duration=CLIMATE_DURATION,
        )
        self._optimistic_hvac_mode = HVACMode.HEAT_COOL
        self.async_write_ha_state()

    async def _async_stop_climate(self) -> None:
        """Stop climate pre-conditioning."""
        service_parameters = [
            {"key": "rce.conditioner", "value": "1"},
        ]
        await self.coordinator.async_send_vehicle_command(
            self._vin,
            SERVICE_ID_CLIMATE,
            "stop",
            service_parameters,
            duration=CLIMATE_DURATION,
        )
        self._optimistic_hvac_mode = HVACMode.OFF
        self.async_write_ha_state()

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator — clear optimistic state."""
        self._optimistic_hvac_mode = None
        super()._handle_coordinator_update()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available and self._vin in self.coordinator.data
