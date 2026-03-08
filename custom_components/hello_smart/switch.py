"""Switch entities for the Hello Smart integration."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SERVICE_ID_CHARGING, SERVICE_ID_FRIDGE
from .coordinator import SmartDataCoordinator
from .models import ChargingState, VehicleData


@dataclass(frozen=True, kw_only=True)
class SmartSwitchEntityDescription(SwitchEntityDescription):
    """Describes a Hello Smart switch entity."""

    turn_on_fn: Callable[[SmartDataCoordinator, str], Coroutine[Any, Any, None]]
    turn_off_fn: Callable[[SmartDataCoordinator, str], Coroutine[Any, Any, None]]
    is_on_fn: Callable[[VehicleData], bool | None]
    available_fn: Callable[[VehicleData], bool]


async def _charging_start(coordinator: SmartDataCoordinator, vin: str) -> None:
    await coordinator.async_send_vehicle_command(
        vin,
        SERVICE_ID_CHARGING,
        "start",
        [{"key": "operation", "value": "1"}, {"key": "rcs.restart", "value": "1"}],
    )


async def _charging_stop(coordinator: SmartDataCoordinator, vin: str) -> None:
    # Charging: command is always "start", serviceParameters control the action
    await coordinator.async_send_vehicle_command(
        vin,
        SERVICE_ID_CHARGING,
        "start",
        [{"key": "operation", "value": "0"}, {"key": "rcs.terminate", "value": "1"}],
    )


def _charging_is_on(data: VehicleData) -> bool | None:
    if data.status.charging_state == ChargingState.NOT_CHARGING:
        return False
    if data.status.charging_state in (
        ChargingState.AC_CHARGING,
        ChargingState.DC_CHARGING,
        ChargingState.CHARGE_PREPARATION,
    ):
        return True
    return False


async def _fridge_on(coordinator: SmartDataCoordinator, vin: str) -> None:
    await coordinator.async_send_vehicle_command(
        vin,
        SERVICE_ID_FRIDGE,
        "start",
        [{"key": "ufr.status", "value": "1"}],
    )


async def _fridge_off(coordinator: SmartDataCoordinator, vin: str) -> None:
    await coordinator.async_send_vehicle_command(
        vin,
        SERVICE_ID_FRIDGE,
        "stop",
        [{"key": "ufr.status", "value": "0"}],
    )


async def _fragrance_on(coordinator: SmartDataCoordinator, vin: str) -> None:
    # Fragrance service ID TBD — using generic telematics command
    await coordinator.async_send_vehicle_command(
        vin, "RFD_2", "start", [{"key": "rfd.status", "value": "1"}]
    )


async def _fragrance_off(coordinator: SmartDataCoordinator, vin: str) -> None:
    await coordinator.async_send_vehicle_command(
        vin, "RFD_2", "stop", [{"key": "rfd.status", "value": "0"}]
    )


async def _vtm_on(coordinator: SmartDataCoordinator, vin: str) -> None:
    await coordinator.async_send_vehicle_command(
        vin, "VTM", "start", [{"key": "vtm.enabled", "value": "1"}]
    )


async def _vtm_off(coordinator: SmartDataCoordinator, vin: str) -> None:
    await coordinator.async_send_vehicle_command(
        vin, "VTM", "stop", [{"key": "vtm.enabled", "value": "0"}]
    )


async def _climate_schedule_on(coordinator: SmartDataCoordinator, vin: str) -> None:
    account = coordinator.account
    if account is None:
        return
    await coordinator._api.async_set_climate_schedule(
        account, vin, {"enabled": True}
    )


async def _climate_schedule_off(coordinator: SmartDataCoordinator, vin: str) -> None:
    account = coordinator.account
    if account is None:
        return
    await coordinator._api.async_set_climate_schedule(
        account, vin, {"enabled": False}
    )


SWITCH_DESCRIPTIONS: list[SmartSwitchEntityDescription] = [
    SmartSwitchEntityDescription(
        key="smart_charging",
        translation_key="smart_charging",
        icon="mdi:ev-station",
        turn_on_fn=_charging_start,
        turn_off_fn=_charging_stop,
        is_on_fn=_charging_is_on,
        available_fn=lambda data: data.status is not None,
    ),
    SmartSwitchEntityDescription(
        key="smart_fridge",
        translation_key="smart_fridge",
        icon="mdi:fridge",
        turn_on_fn=_fridge_on,
        turn_off_fn=_fridge_off,
        is_on_fn=lambda data: data.fridge.active if data.fridge else None,
        available_fn=lambda data: data.fridge is not None,
    ),
    SmartSwitchEntityDescription(
        key="smart_fragrance",
        translation_key="smart_fragrance",
        icon="mdi:scent",
        turn_on_fn=_fragrance_on,
        turn_off_fn=_fragrance_off,
        is_on_fn=lambda data: data.fragrance.active if data.fragrance else None,
        available_fn=lambda data: data.fragrance is not None,
    ),
    SmartSwitchEntityDescription(
        key="smart_vtm",
        translation_key="smart_vtm",
        icon="mdi:shield-car",
        turn_on_fn=_vtm_on,
        turn_off_fn=_vtm_off,
        is_on_fn=lambda data: data.vtm.enabled if data.vtm else None,
        available_fn=lambda data: data.vtm is not None,
    ),
    SmartSwitchEntityDescription(
        key="smart_climate_schedule",
        translation_key="smart_climate_schedule",
        icon="mdi:calendar-clock",
        turn_on_fn=_climate_schedule_on,
        turn_off_fn=_climate_schedule_off,
        is_on_fn=lambda data: data.climate_schedule.enabled if data.climate_schedule else None,
        available_fn=lambda data: data.climate_schedule is not None,
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hello Smart switch entities from a config entry."""
    coordinator: SmartDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SmartSwitch] = []
    for vin, vehicle_data in coordinator.data.items():
        for description in SWITCH_DESCRIPTIONS:
            if not description.available_fn(vehicle_data):
                continue
            entities.append(
                SmartSwitch(
                    coordinator=coordinator,
                    description=description,
                    vin=vin,
                )
            )

    async_add_entities(entities)


class SmartSwitch(CoordinatorEntity[SmartDataCoordinator], SwitchEntity):
    """Representation of a Hello Smart switch."""

    entity_description: SmartSwitchEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SmartDataCoordinator,
        description: SmartSwitchEntityDescription,
        vin: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.entity_description = description
        self._vin = vin
        self._attr_unique_id = f"{vin}_{description.key}"
        self._attr_device_info = coordinator.get_device_info(vin)
        self._optimistic_state: bool | None = None

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on."""
        if self._optimistic_state is not None:
            return self._optimistic_state
        data = self.coordinator.data.get(self._vin)
        if data is None:
            return None
        return self.entity_description.is_on_fn(data)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.entity_description.turn_on_fn(self.coordinator, self._vin)
        self._optimistic_state = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.entity_description.turn_off_fn(self.coordinator, self._vin)
        self._optimistic_state = False
        self.async_write_ha_state()

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator — clear optimistic state."""
        self._optimistic_state = None
        super()._handle_coordinator_update()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        if not super().available:
            return False
        data = self.coordinator.data.get(self._vin)
        if data is None:
            return False
        return self.entity_description.available_fn(data)
