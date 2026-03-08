"""Number entities for the Hello Smart integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SmartDataCoordinator
from .models import VehicleData


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hello Smart number entities from a config entry."""
    coordinator: SmartDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SmartNumber] = []
    for vin, vehicle_data in coordinator.data.items():
        if vehicle_data.charging_reservation is not None:
            entities.append(SmartTargetSOC(coordinator=coordinator, vin=vin))

    async_add_entities(entities)


class SmartNumber(CoordinatorEntity[SmartDataCoordinator], NumberEntity):
    """Base class for Hello Smart number entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SmartDataCoordinator,
        vin: str,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._vin = vin
        self._attr_device_info = coordinator.get_device_info(vin)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return super().available and self._vin in self.coordinator.data


class SmartTargetSOC(SmartNumber):
    """Target State of Charge slider."""

    _attr_translation_key = "smart_target_soc"
    _attr_icon = "mdi:battery-charging-80"
    _attr_native_min_value = 50
    _attr_native_max_value = 100
    _attr_native_step = 5
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(
        self,
        coordinator: SmartDataCoordinator,
        vin: str,
    ) -> None:
        """Initialize the target SOC entity."""
        super().__init__(coordinator, vin)
        self._attr_unique_id = f"{vin}_smart_target_soc"

    @property
    def native_value(self) -> float | None:
        """Return the current target SOC value."""
        data = self.coordinator.data.get(self._vin)
        if data is None or data.charging_reservation is None:
            return None
        return data.charging_reservation.target_soc

    async def async_set_native_value(self, value: float) -> None:
        """Set the target SOC."""
        account = self.coordinator.account
        if account is None:
            return
        await self.coordinator._api.async_set_charging_reservation(
            account, self._vin, {"targetSoc": int(value)}
        )
        # Optimistic update
        data = self.coordinator.data.get(self._vin)
        if data and data.charging_reservation:
            data.charging_reservation.target_soc = int(value)
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        if not super().available:
            return False
        data = self.coordinator.data.get(self._vin)
        return data is not None and data.charging_reservation is not None
