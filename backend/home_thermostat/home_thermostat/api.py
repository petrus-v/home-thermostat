from typing import List, TYPE_CHECKING, Union, Type
from .schemas.devices import RelayState, ThermometerState, FuelGauge
from starlette.requests import Request

if TYPE_CHECKING:
    from anyblok import registry


def device_relay_state(
    code: str, request: "Request"
) -> "registry.Iot.State.Relay":
    """HTTP GET"""
    registry = request.state.anyblok_registry
    return get_device_state(registry, code, registry.Iot.State.Relay)


def device_fuel_gauge_state(
    code: str, request: "Request"
) -> "registry.Iot.State.FuelGauge":
    """HTTP GET"""
    registry = request.state.anyblok_registry
    return get_device_state(registry, code, registry.Iot.State.FuelGauge)


def device_thermometer_state(
    code: str, request: "Request"
) -> "registry.Iot.State.Thermometer":
    """HTTP GET"""
    registry = request.state.anyblok_registry
    return get_device_state(registry, code, registry.Iot.State.Thermometer)


def device_relay_desired_state(
    code: str, request: "Request"
) -> "registry.Iot.State.DesiredRelay":
    registry = request.state.anyblok_registry
    return get_device_state(registry, code, registry.Iot.State.DesiredRelay)


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


def save_device_relay_state(
    code: str, state: RelayState, request: "Request"
) -> "registry.Iot.State.Relay":
    registry = request.state.anyblok_registry
    return set_device_state(registry, code, state, registry.Iot.State.Relay)


def save_device_fuel_gauge_state(
    code: str, state: FuelGauge, request: "Request"
) -> "registry.Iot.State.FuelGauge":
    registry = request.state.anyblok_registry
    return set_device_state(registry, code, state, registry.Iot.State.FuelGauge)


def save_device_thermometer_state(
    code: str, state: ThermometerState, request: "Request"
) -> "registry.Iot.State.Thermometer":
    registry = request.state.anyblok_registry
    return set_device_state(
        registry, code, state, registry.Iot.State.Thermometer
    )


def set_device_state(
    registry: "registry",
    code: str,
    state: Union[RelayState, ThermometerState, FuelGauge],
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


def save_device_relay_desired_state(
    code: str, state: RelayState, request: "Request"
) -> "registry.Iot.State.DesiredRelay":
    registry = request.state.anyblok_registry
    return set_device_state(
        registry, code, state, registry.Iot.State.DesiredRelay
    )
