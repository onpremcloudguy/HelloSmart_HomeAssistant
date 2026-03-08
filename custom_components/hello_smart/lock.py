"""Lock entities for the Hello Smart integration."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any

from homeassistant.components.lock import LockEntity, LockEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SERVICE_ID_DOOR_LOCK, SERVICE_ID_DOOR_UNLOCK
from .coordinator import SmartDataCoordinator
from .models import VehicleData


@dataclass(frozen=True, kw_only=True)
class SmartLockEntityDescription(LockEntityDescription):
    """Describes a Hello Smart lock entity."""

    lock_fn: Callable[[SmartDataCoordinator, str], Coroutine[Any, Any, None]]
    unlock_fn: Callable[[SmartDataCoordinator, str], Coroutine[Any, Any, None]]
    is_locked_fn: Callable[[VehicleData], bool | None]
    available_fn: Callable[[VehicleData], bool]


async def _lock_doors(coordinator: SmartDataCoordinator, vin: str) -> None:
    await coordinator.async_send_vehicle_command(
        vin, SERVICE_ID_DOOR_LOCK, "start", []
    )


async def _unlock_doors(coordinator: SmartDataCoordinator, vin: str) -> None:
    await coordinator.async_send_vehicle_command(
        vin, SERVICE_ID_DOOR_UNLOCK, "start", []
    )


def _doors_locked(data: VehicleData) -> bool | None:
    if not data.status.doors:
        return None
    # All doors closed = locked (door values: True=open, False=closed)
    return not any(data.status.doors.values())


async def _lock_locker(coordinator: SmartDataCoordinator, vin: str) -> None:
    # Locker lock service ID TBD — using generic telematics command
    await coordinator.async_send_vehicle_command(
        vin, "RPC", "start", [{"key": "rpc.lock", "value": "1"}]
    )


async def _unlock_locker(coordinator: SmartDataCoordinator, vin: str) -> None:
    await coordinator.async_send_vehicle_command(
        vin, "RPC", "start", [{"key": "rpc.unlock", "value": "1"}]
    )


LOCK_DESCRIPTIONS: tuple[SmartLockEntityDescription, ...] = (
    SmartLockEntityDescription(
        key="smart_door_lock",
        translation_key="smart_door_lock",
        lock_fn=_lock_doors,
        unlock_fn=_unlock_doors,
        is_locked_fn=_doors_locked,
        available_fn=lambda data: bool(data.status.doors),
    ),
    SmartLockEntityDescription(
        key="smart_trunk_locker",
        translation_key="smart_trunk_locker",
        icon="mdi:lock",
        lock_fn=_lock_locker,
        unlock_fn=_unlock_locker,
        is_locked_fn=lambda data: data.locker.locked if data.locker else None,
        available_fn=lambda data: data.locker is not None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hello Smart lock entities from a config entry."""
    coordinator: SmartDataCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SmartLock] = []
    for vin, vehicle_data in coordinator.data.items():
        for description in LOCK_DESCRIPTIONS:
            if not description.available_fn(vehicle_data):
                continue
            entities.append(
                SmartLock(
                    coordinator=coordinator,
                    description=description,
                    vin=vin,
                )
            )

    async_add_entities(entities)


class SmartLock(CoordinatorEntity[SmartDataCoordinator], LockEntity):
    """Representation of a Hello Smart lock."""

    entity_description: SmartLockEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SmartDataCoordinator,
        description: SmartLockEntityDescription,
        vin: str,
    ) -> None:
        """Initialize the lock."""
        super().__init__(coordinator)
        self.entity_description = description
        self._vin = vin
        self._attr_unique_id = f"{vin}_{description.key}"
        self._attr_device_info = coordinator.get_device_info(vin)
        self._optimistic_locked: bool | None = None

    @property
    def is_locked(self) -> bool | None:
        """Return true if the lock is locked."""
        if self._optimistic_locked is not None:
            return self._optimistic_locked
        data = self.coordinator.data.get(self._vin)
        if data is None:
            return None
        return self.entity_description.is_locked_fn(data)

    async def async_lock(self, **kwargs: Any) -> None:
        """Lock the vehicle doors."""
        await self.entity_description.lock_fn(self.coordinator, self._vin)
        self._optimistic_locked = True
        self.async_write_ha_state()

    async def async_unlock(self, **kwargs: Any) -> None:
        """Unlock the vehicle doors."""
        await self.entity_description.unlock_fn(self.coordinator, self._vin)
        self._optimistic_locked = False
        self.async_write_ha_state()

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator — clear optimistic state."""
        self._optimistic_locked = None
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
