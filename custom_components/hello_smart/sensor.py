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
    EntityCategory,
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfLength,
    UnitOfPower,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SmartDataCoordinator
from .models import ChargingState, PowerMode, VehicleData


@dataclass(frozen=True, kw_only=True)
class SmartSensorEntityDescription(SensorEntityDescription):
    """Describes a Hello Smart sensor entity."""

    value_fn: Callable[[VehicleData], Any]


SENSOR_DESCRIPTIONS: tuple[SmartSensorEntityDescription, ...] = (
    # ── Charging & Battery ──────────────────────────────────────────────
    SmartSensorEntityDescription(
        key="battery_level",
        translation_key="battery_level",
        icon="mdi:car-battery",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.status.battery_level,
    ),
    SmartSensorEntityDescription(
        key="range_remaining",
        translation_key="range_remaining",
        icon="mdi:map-marker-distance",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: data.status.range_remaining,
    ),
    SmartSensorEntityDescription(
        key="charging_status",
        translation_key="charging_status",
        icon="mdi:ev-station",
        device_class=SensorDeviceClass.ENUM,
        options=[state.value for state in ChargingState],
        value_fn=lambda data: data.status.charging_state.value,
    ),
    SmartSensorEntityDescription(
        key="charge_voltage",
        translation_key="charge_voltage",
        icon="mdi:flash",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.status.charge_voltage or 0,
    ),
    SmartSensorEntityDescription(
        key="charge_current",
        translation_key="charge_current",
        icon="mdi:current-ac",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.status.charge_current or 0,
    ),
    SmartSensorEntityDescription(
        key="time_to_full",
        translation_key="time_to_full",
        icon="mdi:battery-clock",
        native_unit_of_measurement=UnitOfTime.MINUTES,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.status.time_to_full or 0,
    ),
    # ── Firmware ───────────────────────────────────────────────────────
    SmartSensorEntityDescription(
        key="current_firmware_version",
        translation_key="current_firmware_version",
        icon="mdi:package-up",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.ota.current_version or "unknown",
    ),
    SmartSensorEntityDescription(
        key="target_firmware_version",
        translation_key="target_firmware_version",
        icon="mdi:package-down",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.ota.target_version or "unknown",
    ),
    # ── Tyres ──────────────────────────────────────────────────────────
    SmartSensorEntityDescription(
        key="tyre_pressure_fl",
        translation_key="tyre_pressure_fl",
        icon="mdi:car-tire-alert",
        native_unit_of_measurement=UnitOfPressure.KPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: data.status.tyre_pressure_fl,
    ),
    SmartSensorEntityDescription(
        key="tyre_pressure_fr",
        translation_key="tyre_pressure_fr",
        icon="mdi:car-tire-alert",
        native_unit_of_measurement=UnitOfPressure.KPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: data.status.tyre_pressure_fr,
    ),
    SmartSensorEntityDescription(
        key="tyre_pressure_rl",
        translation_key="tyre_pressure_rl",
        icon="mdi:car-tire-alert",
        native_unit_of_measurement=UnitOfPressure.KPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: data.status.tyre_pressure_rl,
    ),
    SmartSensorEntityDescription(
        key="tyre_pressure_rr",
        translation_key="tyre_pressure_rr",
        icon="mdi:car-tire-alert",
        native_unit_of_measurement=UnitOfPressure.KPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: data.status.tyre_pressure_rr,
    ),
    SmartSensorEntityDescription(
        key="tyre_temp_fl",
        translation_key="tyre_temp_fl",
        icon="mdi:tire",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.tyre_temp_fl,
    ),
    SmartSensorEntityDescription(
        key="tyre_temp_fr",
        translation_key="tyre_temp_fr",
        icon="mdi:tire",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.tyre_temp_fr,
    ),
    SmartSensorEntityDescription(
        key="tyre_temp_rl",
        translation_key="tyre_temp_rl",
        icon="mdi:tire",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.tyre_temp_rl,
    ),
    SmartSensorEntityDescription(
        key="tyre_temp_rr",
        translation_key="tyre_temp_rr",
        icon="mdi:tire",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.tyre_temp_rr,
    ),
    # ── Maintenance ────────────────────────────────────────────────────
    SmartSensorEntityDescription(
        key="odometer",
        translation_key="odometer",
        icon="mdi:counter",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=0,
        value_fn=lambda data: data.status.odometer,
    ),
    SmartSensorEntityDescription(
        key="days_to_service",
        translation_key="days_to_service",
        icon="mdi:wrench-clock",
        native_unit_of_measurement=UnitOfTime.DAYS,
        device_class=SensorDeviceClass.DURATION,
        value_fn=lambda data: data.status.days_to_service,
    ),
    SmartSensorEntityDescription(
        key="distance_to_service",
        translation_key="distance_to_service",
        icon="mdi:road-variant",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        suggested_display_precision=0,
        value_fn=lambda data: data.status.distance_to_service,
    ),
    # ── 12V Battery ────────────────────────────────────────────────────
    SmartSensorEntityDescription(
        key="battery_12v_voltage",
        translation_key="battery_12v_voltage",
        icon="mdi:car-battery",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.status.battery_12v_voltage,
    ),
    SmartSensorEntityDescription(
        key="battery_12v_level",
        translation_key="battery_12v_level",
        icon="mdi:car-battery",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.status.battery_12v_level,
    ),
    # ── Climate ────────────────────────────────────────────────────────
    SmartSensorEntityDescription(
        key="interior_temp",
        translation_key="interior_temp",
        icon="mdi:thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.status.interior_temp,
    ),
    SmartSensorEntityDescription(
        key="exterior_temp",
        translation_key="exterior_temp",
        icon="mdi:sun-thermometer",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.status.exterior_temp,
    ),
    # ── Vehicle State ─────────────────────────────────────────────────
    SmartSensorEntityDescription(
        key="power_mode",
        translation_key="power_mode",
        icon="mdi:power",
        device_class=SensorDeviceClass.ENUM,
        options=[mode.value for mode in PowerMode],
        value_fn=lambda data: (
            data.status.power_mode.value if data.status.power_mode
            else (data.running_state.power_mode.value if data.running_state else PowerMode.OFF.value)
        ),
    ),
    SmartSensorEntityDescription(
        key="speed",
        translation_key="speed",
        icon="mdi:speedometer",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: data.running_state.speed if data.running_state else 0,
    ),
    # ── Charging Schedule ──────────────────────────────────────────────
    SmartSensorEntityDescription(
        key="charging_schedule_status",
        translation_key="charging_schedule_status",
        icon="mdi:calendar-clock",
        device_class=SensorDeviceClass.ENUM,
        options=["active", "inactive"],
        value_fn=lambda data: (
            "active" if data.charging_reservation and data.charging_reservation.active
            else "inactive"
        ),
    ),
    SmartSensorEntityDescription(
        key="charging_schedule_start",
        translation_key="charging_schedule_start",
        icon="mdi:clock-start",
        value_fn=lambda data: (
            data.charging_reservation.start_time
            if data.charging_reservation and data.charging_reservation.start_time
            else ""
        ),
    ),
    SmartSensorEntityDescription(
        key="charging_schedule_end",
        translation_key="charging_schedule_end",
        icon="mdi:clock-end",
        value_fn=lambda data: (
            data.charging_reservation.end_time
            if data.charging_reservation and data.charging_reservation.end_time
            else ""
        ),
    ),
    SmartSensorEntityDescription(
        key="charging_target_soc",
        translation_key="charging_target_soc",
        icon="mdi:battery-charging-high",
        native_unit_of_measurement=PERCENTAGE,
        value_fn=lambda data: (
            data.charging_reservation.target_soc
            if data.charging_reservation and data.charging_reservation.target_soc is not None
            else 0
        ),
    ),
    # ── Climate Schedule ──────────────────────────────────────────────
    SmartSensorEntityDescription(
        key="climate_schedule_status",
        translation_key="climate_schedule_status",
        icon="mdi:air-conditioner",
        device_class=SensorDeviceClass.ENUM,
        options=["enabled", "disabled"],
        value_fn=lambda data: (
            "enabled" if data.climate_schedule and data.climate_schedule.enabled
            else "disabled"
        ),
    ),
    SmartSensorEntityDescription(
        key="climate_schedule_time",
        translation_key="climate_schedule_time",
        icon="mdi:clock-outline",
        value_fn=lambda data: (
            data.climate_schedule.scheduled_time
            if data.climate_schedule and data.climate_schedule.scheduled_time
            else ""
        ),
    ),
    # ── Trip Journal ────────────────────────────────────────────────────
    SmartSensorEntityDescription(
        key="last_trip_distance",
        translation_key="last_trip_distance",
        icon="mdi:map-marker-path",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.last_trip.distance if data.last_trip else 0,
    ),
    SmartSensorEntityDescription(
        key="last_trip_duration",
        translation_key="last_trip_duration",
        icon="mdi:timer-outline",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        value_fn=lambda data: data.last_trip.duration if data.last_trip else 0,
    ),
    SmartSensorEntityDescription(
        key="last_trip_energy",
        translation_key="last_trip_energy",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=1,
        value_fn=lambda data: data.last_trip.energy_consumption if data.last_trip else 0,
    ),
    SmartSensorEntityDescription(
        key="last_trip_avg_consumption",
        translation_key="last_trip_avg_consumption",
        icon="mdi:leaf",
        native_unit_of_measurement="kWh/100km",
        suggested_display_precision=1,
        value_fn=lambda data: data.last_trip.avg_energy_consumption if data.last_trip else 0,
    ),
    SmartSensorEntityDescription(
        key="total_distance",
        translation_key="total_distance",
        icon="mdi:counter",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=0,
        value_fn=lambda data: data.total_distance or 0,
    ),
    SmartSensorEntityDescription(
        key="energy_ranking",
        translation_key="energy_ranking",
        icon="mdi:podium",
        value_fn=lambda data: data.energy_ranking.my_ranking if data.energy_ranking else 0,
    ),
    # ── Accessories ─────────────────────────────────────────────────────
    SmartSensorEntityDescription(
        key="fridge_temperature",
        translation_key="fridge_temperature",
        icon="mdi:fridge-outline",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.fridge.temperature if data.fridge else 0,
    ),
    SmartSensorEntityDescription(
        key="fragrance_level",
        translation_key="fragrance_level",
        icon="mdi:spray",
        value_fn=lambda data: (
            data.fragrance.level
            if data.fragrance and data.fragrance.level
            else ""
        ),
    ),
    # ── Security & Geofences ───────────────────────────────────────────
    SmartSensorEntityDescription(
        key="geofence_count",
        translation_key="geofence_count",
        icon="mdi:map-marker-radius",
        value_fn=lambda data: data.geofence.count if data.geofence else 0,
    ),
    SmartSensorEntityDescription(
        key="last_trip_avg_speed",
        translation_key="last_trip_avg_speed",
        icon="mdi:speedometer-medium",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: data.last_trip.avg_speed if data.last_trip else 0,
    ),
    SmartSensorEntityDescription(
        key="last_trip_max_speed",
        translation_key="last_trip_max_speed",
        icon="mdi:speedometer",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: data.last_trip.max_speed if data.last_trip else 0,
    ),
    SmartSensorEntityDescription(
        key="climate_schedule_temp",
        translation_key="climate_schedule_temp",
        icon="mdi:air-conditioner",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        value_fn=lambda data: (
            data.climate_schedule.temperature
            if data.climate_schedule
            else 0
        ),
    ),
    SmartSensorEntityDescription(
        key="climate_schedule_duration",
        translation_key="climate_schedule_duration",
        icon="mdi:timer-sand",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        value_fn=lambda data: (
            data.climate_schedule.duration
            if data.climate_schedule
            else 0
        ),
    ),
    SmartSensorEntityDescription(
        key="fridge_mode",
        translation_key="fridge_mode",
        icon="mdi:fridge",
        device_class=SensorDeviceClass.ENUM,
        options=["cooling", "warming", "off"],
        value_fn=lambda data: data.fridge.mode if data.fridge and data.fridge.mode else "off",
    ),
    # ── Diagnostics ────────────────────────────────────────────────────
    SmartSensorEntityDescription(
        key="diagnostic_status",
        translation_key="diagnostic_status",
        icon="mdi:car-wrench",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.diagnostic.status if data.diagnostic and data.diagnostic.status else "ok",
    ),
    SmartSensorEntityDescription(
        key="diagnostic_code",
        translation_key="diagnostic_code",
        icon="mdi:alert-circle-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.diagnostic.dtc_code if data.diagnostic and data.diagnostic.dtc_code else "",
    ),
    SmartSensorEntityDescription(
        key="backup_battery_voltage",
        translation_key="backup_battery_voltage",
        icon="mdi:battery-outline",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.telematics.backup_battery_voltage if data.telematics else 0,
    ),
    SmartSensorEntityDescription(
        key="backup_battery_level",
        translation_key="backup_battery_level",
        icon="mdi:battery-outline",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.telematics.backup_battery_level if data.telematics else 0,
    ),
    SmartSensorEntityDescription(
        key="capability_count",
        translation_key="capability_count",
        icon="mdi:format-list-checks",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
        value_fn=lambda data: len(data.capabilities.service_ids) if data.capabilities else 0,
    ),
    SmartSensorEntityDescription(
        key="washer_fluid_level",
        translation_key="washer_fluid_level",
        icon="mdi:wiper-wash",
        value_fn=lambda data: data.status.washer_fluid_level,
    ),
    SmartSensorEntityDescription(
        key="fota_pending_count",
        translation_key="fota_pending_count",
        icon="mdi:cellphone-arrow-down",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.fota_notification.pending_count if data.fota_notification else 0,
    ),
    # ── Running Status ─────────────────────────────────────────────────
    SmartSensorEntityDescription(
        key="trip_meter_1",
        translation_key="trip_meter_1",
        icon="mdi:counter",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
        value_fn=lambda data: data.status.trip_meter_1,
    ),
    SmartSensorEntityDescription(
        key="trip_meter_2",
        translation_key="trip_meter_2",
        icon="mdi:counter",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
        value_fn=lambda data: data.status.trip_meter_2,
    ),
    SmartSensorEntityDescription(
        key="average_speed",
        translation_key="average_speed",
        icon="mdi:speedometer-medium",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.SPEED,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: data.status.average_speed,
    ),
    SmartSensorEntityDescription(
        key="engine_coolant_level",
        translation_key="engine_coolant_level",
        icon="mdi:car-coolant-level",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.status.engine_coolant_level,
    ),
    # ── EV Additional ──────────────────────────────────────────────────
    SmartSensorEntityDescription(
        key="range_at_full_charge",
        translation_key="range_at_full_charge",
        icon="mdi:map-marker-distance",
        native_unit_of_measurement=UnitOfLength.KILOMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=lambda data: data.status.range_at_full_charge,
    ),
    SmartSensorEntityDescription(
        key="average_power_consumption",
        translation_key="average_power_consumption",
        icon="mdi:leaf",
        native_unit_of_measurement="Wh/km",
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: (
            abs(data.status.average_power_consumption)
            if data.status.average_power_consumption is not None
            else 0
        ),
    ),
    SmartSensorEntityDescription(
        key="dc_charge_current",
        translation_key="dc_charge_current",
        icon="mdi:current-dc",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        value_fn=lambda data: data.status.dc_charge_current or 0,
    ),
    SmartSensorEntityDescription(
        key="charging_power",
        translation_key="charging_power",
        icon="mdi:flash",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        value_fn=lambda data: data.status.charging_power or 0,
    ),
    # ── Climate Detailed ───────────────────────────────────────────────
    SmartSensorEntityDescription(
        key="window_position_driver",
        translation_key="window_position_driver",
        icon="mdi:car-door",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.window_position_driver,
    ),
    SmartSensorEntityDescription(
        key="window_position_passenger",
        translation_key="window_position_passenger",
        icon="mdi:car-door",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.window_position_passenger,
    ),
    SmartSensorEntityDescription(
        key="window_position_driver_rear",
        translation_key="window_position_driver_rear",
        icon="mdi:car-door",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.window_position_driver_rear,
    ),
    SmartSensorEntityDescription(
        key="window_position_passenger_rear",
        translation_key="window_position_passenger_rear",
        icon="mdi:car-door",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.window_position_passenger_rear,
    ),
    SmartSensorEntityDescription(
        key="sunroof_position",
        translation_key="sunroof_position",
        icon="mdi:window-open-variant",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.sunroof_position,
    ),
    SmartSensorEntityDescription(
        key="curtain_position",
        translation_key="curtain_position",
        icon="mdi:curtains",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.curtain_position,
    ),
    SmartSensorEntityDescription(
        key="sun_curtain_rear_position",
        translation_key="sun_curtain_rear_position",
        icon="mdi:curtains",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.sun_curtain_rear_position,
    ),
    # ── Seat Heating / Ventilation ─────────────────────────────────────
    SmartSensorEntityDescription(
        key="driver_seat_heating",
        translation_key="driver_seat_heating",
        icon="mdi:car-seat-heater",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.status.driver_seat_heating,
    ),
    SmartSensorEntityDescription(
        key="passenger_seat_heating",
        translation_key="passenger_seat_heating",
        icon="mdi:car-seat-heater",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.status.passenger_seat_heating,
    ),
    SmartSensorEntityDescription(
        key="rear_left_seat_heating",
        translation_key="rear_left_seat_heating",
        icon="mdi:car-seat-heater",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.rear_left_seat_heating,
    ),
    SmartSensorEntityDescription(
        key="rear_right_seat_heating",
        translation_key="rear_right_seat_heating",
        icon="mdi:car-seat-heater",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.rear_right_seat_heating,
    ),
    SmartSensorEntityDescription(
        key="driver_seat_ventilation",
        translation_key="driver_seat_ventilation",
        icon="mdi:car-seat-cooler",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.status.driver_seat_ventilation,
    ),
    SmartSensorEntityDescription(
        key="passenger_seat_ventilation",
        translation_key="passenger_seat_ventilation",
        icon="mdi:car-seat-cooler",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.status.passenger_seat_ventilation,
    ),
    SmartSensorEntityDescription(
        key="rear_left_seat_ventilation",
        translation_key="rear_left_seat_ventilation",
        icon="mdi:car-seat-cooler",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.rear_left_seat_ventilation,
    ),
    SmartSensorEntityDescription(
        key="rear_right_seat_ventilation",
        translation_key="rear_right_seat_ventilation",
        icon="mdi:car-seat-cooler",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.rear_right_seat_ventilation,
    ),
    SmartSensorEntityDescription(
        key="steering_wheel_heating",
        translation_key="steering_wheel_heating",
        icon="mdi:steering",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.status.steering_wheel_heating,
    ),
    # ── Pollution / Air Quality ────────────────────────────────────────
    SmartSensorEntityDescription(
        key="interior_pm25",
        translation_key="interior_pm25",
        icon="mdi:blur",
        native_unit_of_measurement="µg/m³",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.status.interior_pm25,
    ),
    SmartSensorEntityDescription(
        key="interior_pm25_level",
        translation_key="interior_pm25_level",
        icon="mdi:air-filter",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.interior_pm25_level,
    ),
    SmartSensorEntityDescription(
        key="exterior_pm25_level",
        translation_key="exterior_pm25_level",
        icon="mdi:air-filter",
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        value_fn=lambda data: data.status.exterior_pm25_level,
    ),
    SmartSensorEntityDescription(
        key="relative_humidity",
        translation_key="relative_humidity",
        icon="mdi:water-percent",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.status.relative_humidity,
    ),
    # ── Maintenance Additional ─────────────────────────────────────────
    SmartSensorEntityDescription(
        key="engine_hours_to_service",
        translation_key="engine_hours_to_service",
        icon="mdi:engine-outline",
        native_unit_of_measurement=UnitOfTime.HOURS,
        device_class=SensorDeviceClass.DURATION,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.status.engine_hours_to_service,
    ),
    SmartSensorEntityDescription(
        key="service_warning",
        translation_key="service_warning",
        icon="mdi:alert-circle",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.status.service_warning,
    ),
    SmartSensorEntityDescription(
        key="battery_12v_state_of_health",
        translation_key="battery_12v_state_of_health",
        icon="mdi:battery-heart-variant",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.status.battery_12v_state_of_health,
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
    for vin, vehicle_data in coordinator.data.items():
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
