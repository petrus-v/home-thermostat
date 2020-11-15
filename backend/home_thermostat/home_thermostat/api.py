from typing import List, TYPE_CHECKING, Union, Type
from .schemas.devices import RelayState, ThermometerState, FuelGaugeState
from starlette.requests import Request
from fastapi import Depends
from anyblok_fastapi.fastapi import get_registry, registry_transaction
from anyblok.registry import Registry
from sqlalchemy.orm import contains_eager
import time
from home_thermostat.home_thermostat.common import ThermostatMode as Mode
from home_thermostat.home_thermostat.schemas.devices import (
    RelayState, ThermometerState, FuelGaugeState, ThermostatMode, ThermostatRange
)

if TYPE_CHECKING:
    from anyblok import registry


def device_relay_state(
    code: str,
    ab_registry: "Registry" = Depends(get_registry),
) -> RelayState:
    """HTTP GET"""
    with registry_transaction(ab_registry) as registry:
        return RelayState.from_orm(get_device_state(registry, code, registry.Iot.State.Relay))


def device_relay_desired_state(
    code: str,
    ab_registry: "Registry" = Depends(get_registry),
) -> RelayState:
    with registry_transaction(ab_registry) as registry:
        return RelayState.from_orm(get_device_state(registry, code, registry.Iot.State.DesiredRelay))


def device_fuel_gauge_state(
    code: str,
    ab_registry: "Registry" = Depends(get_registry),
) -> FuelGaugeState:
    """HTTP GET"""
    with registry_transaction(ab_registry) as registry:
        return FuelGaugeState.from_orm(
            get_device_state(registry, code, registry.Iot.State.FuelGauge)
        )


def device_thermometer_state(
    code: str,
    ab_registry: "Registry" = Depends(get_registry),
) -> ThermometerState:
    """HTTP GET"""
    with registry_transaction(ab_registry) as registry:
        return ThermometerState.from_orm(
            get_device_state(registry, code, registry.Iot.State.Thermometer)
        )

def get_device_state(
    registry: "registry",
    code: str,
    State: Type["registry.Iot.State"],
) -> Union[
    "registry.Iot.State.Relay",
    "registry.Iot.State.DesiredRelay",
    "registry.Iot.State.Thermometer",
    "registry.Iot.State.FuelGauge",
]:
    """Cast states.State -> DeviceState is done throught fastAPI"""
    Device = registry.Iot.Device
    state = (
        State.query()
        .join(Device)
        .filter(Device.code == code)
        .order_by(registry.Iot.State.create_date.desc())
        .first()
    )
    if not state:
        device = Device.query().filter_by(code=code).one()
        # We don't wan't to instert a new state here, just creating
        # a default instance
        state = State(device=device)
        registry.flush()
    return state

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
            # We don't wan't to instert a new state range, just creating
            # a default instance
            range_ = registry.Iot.Thermostat.Range()
        return ThermostatRange.from_orm(range_)

def set_thermostat_range(
    code: str,
    thermostat_range: ThermostatRange,
    ab_registry: "Registry" = Depends(get_registry),
) -> ThermostatRange:
    with registry_transaction(ab_registry) as registry:
        return ThermostatRange.from_orm(
            registry.Iot.Thermostat.Range.insert(
                code=code, **dict(thermostat_range)
            )
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
            set_device_state(
                registry, code, state, registry.Iot.State.Thermometer
            )
        )


def save_device_relay_desired_state(
    code: str,
    state: RelayState,
    ab_registry: "Registry" = Depends(get_registry),
) -> RelayState:
    with registry_transaction(ab_registry) as registry:
        return RelayState.from_orm(
            set_device_state(
                registry, code, state, registry.Iot.State.DesiredRelay
            )
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
            mode=registry.System.Parameter.get(
                "mode", default=Mode.manual.value
            )
        )
