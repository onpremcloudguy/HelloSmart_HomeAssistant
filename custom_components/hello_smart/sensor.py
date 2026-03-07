"""Sensor entities for the Hello Smart integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfLength,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SmartDataCoordinator
from .models import ChargingState, VehicleData


@dataclass(frozen=True, kw_only=True)
class SmartSensorEntityDescription(SensorEntityDescription):
    """Describes a Hello Smart sensor entity."""

    value_fn: Callable[[VehicleData], Any]


SENSOR_DESCRIPTIONS: tuple[SmartSensorEntityDescription, ...] = (
    SmartSensorEntityDescription(
        key="battery_level",
        translation_key="battery_level",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.status.battery_level,
    ),
    SmartSensorEntityDescription(
        key="range_remaining",
        translation_key="range_remaining",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.status.range_remaining,
    ),
    SmartSensorEntityDescription(
        key="charging_status",
        translation_key="charging_status",
        device_class=SensorDeviceClass.ENUM,
        options=[state.value for state in ChargingState],
        value_fn=lambda data: data.status.charging_state.value,
    ),
    SmartSensorEntityDescription(
        key="charge_voltage",
        translation_key="charge_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.status.charge_voltage,
    ),
    SmartSensorEntityDescription(
        key="charge_current",
        translation_key="charge_current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.status.charge_current,
    ),
    SmartSensorEntityDescription(
        key="time_to_full",
        translation_key="time_to_full",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.status.time_to_full,
    ),
    SmartSensorEntityDescription(
        key="current_firmware_version",
        translation_key="current_firmware_version",
        value_fn=lambda data: data.ota.current_version or None,
    ),
    SmartSensorEntityDescription(
        key="target_firmware_version",
        translation_key="target_firmware_version",
        value_fn=lambda data: data.ota.target_version or None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hello Smart sensor entities from a config entry."""
    coordinator: SmartDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SmartSensorEntity] = []
    for vin in coordinator.data:
        for description in SENSOR_DESCRIPTIONS:
            entities.append(
                SmartSensorEntity(
                    coordinator=coordinator,
                    description=description,
                    vin=vin,
                )
            )

    async_add_entities(entities)


class SmartSensorEntity(CoordinatorEntity[SmartDataCoordinator], SensorEntity):
    """Representation of a Hello Smart sensor."""

    entity_description: SmartSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SmartDataCoordinator,
        description: SmartSensorEntityDescription,
        vin: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._vin = vin
        self._attr_unique_id = f"{vin}_{description.key}"
        self._attr_device_info = coordinator.get_device_info(vin)

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        data = self.coordinator.data.get(self._vin)
        if data is None:
            return None
        return self.entity_description.value_fn(data)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            super().available
            and self._vin in self.coordinator.data
        )
