from typing import List, TYPE_CHECKING, Union
from .schemas.relay import RelayState
from starlette.requests import Request

if TYPE_CHECKING:
    from anyblok import registry


def device_state(code: str, request: "Request") -> Union[RelayState]:
    registry = request.state.anyblok_registry
    return get_device_state(registry, registry.IOT.State, code)


def device_desired_state(code: str, request: "Request") -> Union[RelayState]:
    registry = request.state.anyblok_registry
    return get_device_state(registry, registry.IOT.DesiredState, code)


def get_device_state(registry, State, code):
    Device = registry.IOT.Device
    state = State.query().join(Device).filter(
        Device.code == code).order_by(State.create_date.desc()).first()
    if not state:
        device = Device.query().filter_by(code=code).one()
        return device.serialyzer()
    return state.device.serialyzer.parse_raw(state.state)


def save_device_state(code: str, state: Union[RelayState], request: "Request"):
    registry = request.state.anyblok_registry
    return set_device_state(registry, registry.IOT.State, code, state)


def save_device_desired_state(code: str, state: Union[RelayState], request: "Request"):
    registry = request.state.anyblok_registry
    return set_device_state(registry, registry.IOT.DesiredState, code, state)


def set_device_state(registry, State, code, state):
    Device = registry.IOT.Device
    device = Device.query().filter(Device.code == code).one()
    State.insert(
        device=device,
        state=state.json()
    )
    return state
