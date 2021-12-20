from datetime import time
from decimal import Decimal as D
from typing import TYPE_CHECKING, Type, Union, Any, Dict

from anyblok.registry import Registry
from anyblok_fastapi.fastapi import get_registry, registry_transaction
from fastapi import Depends

from home_thermostat.home_thermostat.common import ThermostatMode as Mode
from home_thermostat.home_thermostat.schemas.devices import (
    APRSWeatherStationPacket,
    FuelGaugeState,
    RelayState,
    ThermometerState,
    ThermostatMode,
    ThermostatRange,
    WeatherStationState,
)

if TYPE_CHECKING:
    from anyblok import registry


def device_relay_state(
    code: str,
    ab_registry: "Registry" = Depends(get_registry),
) -> RelayState:
    """HTTP GET"""
    with registry_transaction(ab_registry) as registry:
        return RelayState.from_orm(registry.Iot.State.Relay.get_device_state(code))


def device_relay_desired_state(
    code: str,
    ab_registry: "Registry" = Depends(get_registry),
) -> RelayState:
    with registry_transaction(ab_registry) as registry:
        return RelayState.from_orm(
            registry.Iot.State.DesiredRelay.get_device_state(code)
        )


def device_fuel_gauge_state(
    code: str,
    ab_registry: "Registry" = Depends(get_registry),
) -> FuelGaugeState:
    """HTTP GET"""
    with registry_transaction(ab_registry) as registry:
        return FuelGaugeState.from_orm(
            registry.Iot.State.FuelGauge.get_device_state(code)
        )


def device_thermometer_state(
    code: str,
    ab_registry: "Registry" = Depends(get_registry),
) -> ThermometerState:
    """HTTP GET"""
    with registry_transaction(ab_registry) as registry:
        return ThermometerState.from_orm(
            registry.Iot.State.Thermometer.get_device_state(code)
        )


def get_thermostat_range(
    code: str,
    ab_registry: "Registry" = Depends(get_registry),
) -> ThermostatRange:
    with registry_transaction(ab_registry) as registry:

        range_ = (
            registry.Iot.Thermostat.Range.query()
            .filter_by(code=code)
            .order_by(registry.Iot.Thermostat.Range.create_date.desc())
            .first()
        )
        if not range_:
            # We don't want to instert a new state range, just creating
            # a default instance
            range_ = registry.Iot.Thermostat.Range(
                start=time(hour=0, minute=0),
                end=time(hour=23, minute=59),
                celsius=D("16"),
            )
        return ThermostatRange.from_orm(range_)


def set_thermostat_range(
    code: str,
    thermostat_range: ThermostatRange,
    ab_registry: "Registry" = Depends(get_registry),
) -> ThermostatRange:
    with registry_transaction(ab_registry) as registry:
        return ThermostatRange.from_orm(
            registry.Iot.Thermostat.Range.insert(code=code, **dict(thermostat_range))
        )


def save_device_relay_state(
    code: str,
    state: RelayState,
    ab_registry: "Registry" = Depends(get_registry),
) -> RelayState:
    with registry_transaction(ab_registry) as registry:
        return RelayState.from_orm(
            set_device_state(registry, code, state, registry.Iot.State.Relay)
        )


def save_device_fuel_gauge_state(
    code: str,
    state: FuelGaugeState,
    ab_registry: "Registry" = Depends(get_registry),
) -> FuelGaugeState:
    with registry_transaction(ab_registry) as registry:
        return FuelGaugeState.from_orm(
            set_device_state(registry, code, state, registry.Iot.State.FuelGauge)
        )


def save_device_thermometer_state(
    code: str,
    state: ThermometerState,
    ab_registry: "Registry" = Depends(get_registry),
) -> ThermometerState:
    with registry_transaction(ab_registry) as registry:
        return ThermometerState.from_orm(
            set_device_state(registry, code, state, registry.Iot.State.Thermometer)
        )


def save_device_relay_desired_state(
    code: str,
    state: RelayState,
    ab_registry: "Registry" = Depends(get_registry),
) -> RelayState:
    with registry_transaction(ab_registry) as registry:
        return RelayState.from_orm(
            set_device_state(registry, code, state, registry.Iot.State.DesiredRelay)
        )


def set_device_state(
    registry: "registry",
    code: str,
    state: Union[RelayState, ThermometerState, FuelGaugeState],
    State: Type["registry.Iot.State"],
) -> Union[
    "registry.Iot.State.DesiredRelay",
    "registry.Iot.State.Relay",
    "registry.Iot.State.Thermometer",
    "registry.Iot.State.FuelGauge",
    "registry.Iot.State.WeatherStation",
]:
    Device = registry.Iot.Device
    device = Device.query().filter(Device.code == code).one()
    data: Dict[str, Any] = dict(state)
    data["device"] = device
    state = State.insert(**data)
    registry.flush()
    return state


def set_mode(
    mode: ThermostatMode,
    ab_registry: "Registry" = Depends(get_registry),
) -> ThermostatMode:
    with registry_transaction(ab_registry) as registry:
        registry.System.Parameter.set("mode", mode.mode.value)
    return mode


def get_mode(
    ab_registry: "Registry" = Depends(get_registry),
) -> ThermostatMode:
    with registry_transaction(ab_registry) as registry:
        return ThermostatMode(
            mode=registry.System.Parameter.get("mode", default=Mode.manual.value)
        )

def device_weather_station_state(
    code: str,
    ab_registry: "Registry" = Depends(get_registry),
) -> WeatherStationState:

    """HTTP GET"""
    with registry_transaction(ab_registry) as registry:
        return WeatherStationState.from_orm(
            registry.Iot.State.WeatherStation.get_device_state(code)
        )

def save_device_weather_station_state(
    code: str,
    state: WeatherStationState,
    ab_registry: "Registry" = Depends(get_registry),
) -> WeatherStationState:
    with registry_transaction(ab_registry) as registry:
        return WeatherStationState.from_orm(
            set_device_state(registry, code, state, registry.Iot.State.WeatherStation)
        )

def save_device_weather_station_aprs_packet(
    packet: APRSWeatherStationPacket,
    ab_registry: "Registry" = Depends(get_registry),
) -> WeatherStationState:
    state: WeatherStationState = packet.parse()
    with registry_transaction(ab_registry) as registry:
        return WeatherStationState.from_orm(
            set_device_state(
                registry,
                state.station_code,
                state,
                registry.Iot.State.WeatherStation
            )
        )
