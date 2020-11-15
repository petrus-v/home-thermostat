import pytest
from datetime import datetime, time
from decimal import Decimal as D
from home_thermostat.home_thermostat.common import ThermostatMode as Mode


@pytest.fixture(autouse=True)
def thermostat_mode(rollback_registry):
    rollback_registry.System.Parameter.set(
        "mode", Mode.thermostat.value
    )

@pytest.fixture()
def default_range(rollback_registry):
    Range = rollback_registry.Iot.Thermostat.Range
    Range.insert(
        create_date=datetime(2020, 6 , 14),
        code="00",
        start=time(hour=0, minute=0),
        end=time(hour=23, minute=59),
        celsius=D("15"),
    )

@pytest.fixture()
def ranges(rollback_registry, default_range):
    Range = rollback_registry.Iot.Thermostat.Range
    Range.insert(
        create_date=datetime(2020, 6, 15),
        code="10",
        start=time(hour=10, minute=30),
        end=time(hour=12, minute=30),
        celsius=D("18.5"),
    )
    Range.insert(
        create_date=datetime(2020, 6, 15),
        code="15",
        start=time(hour=11, minute=13),
        end=time(hour=11, minute=16),
        celsius=D("19"),
    )
    Range.insert(
        create_date=datetime(2020, 6, 16),
        code="15",
        start=time(hour=11, minute=13),
        end=time(hour=11, minute=16),
        celsius=D("666"),
    )
    rollback_registry.flush()


def test_range(rollback_registry, ranges):
    Range = rollback_registry.Iot.Thermostat.Range
    assert Range.get_desired_living_room_temperature(datetime(2020, 6, 13)) is None
    assert Range.get_desired_living_room_temperature(datetime(2020, 6, 14, 1)) == D("15")
    assert Range.get_desired_living_room_temperature(datetime(2020, 6, 16, 11, 14)) == D("666")
    assert Range.get_desired_living_room_temperature(datetime(2020, 6, 16, 11, 12)) == D("18.5")
    assert Range.get_desired_living_room_temperature(datetime(2020, 6, 15, 11, 14)) == D("19")
    assert Range.get_desired_living_room_temperature(datetime(2020, 6, 15, 11, 12)) == D("18.5")

@pytest.fixture()
def living_room_sensor_data(rollback_registry, living_room):
    registry = rollback_registry
    Thermometer = registry.Iot.State.Thermometer
    Thermometer.insert(
        device=living_room,
        create_date=datetime(2020, 6, 15, 10, 00),
        celsius=D("8.0")
    )
    Thermometer.insert(
        device=living_room,
        create_date=datetime(2020, 6, 15, 11, 00),
        celsius=D("18.0")
    )
    Thermometer.insert(
        device=living_room,
        create_date=datetime(2020, 6, 15, 11, 8),
        celsius=D("20.0")
    )
    registry.flush()



def test_burner_relay_desired_state_no_data(rollback_registry, burner):
    registry = rollback_registry
    state = registry.Iot.State.DesiredRelay.get_device_state(burner.code)
    assert state.is_open is True


def test_burner_relay_desired_state_no_avg(
    rollback_registry, burner, living_room_sensor_data, ranges
):
    """ranges has only old data, now is used if date is not defined"""
    registry = rollback_registry
    state = registry.Iot.State.DesiredRelay.get_device_state(burner.code)
    assert state.is_open is True


def test_burner_relay_desired_state(
    rollback_registry, burner, living_room_sensor_data, ranges
):
    """ranges has only old data, now is used if date is not defined"""
    registry = rollback_registry
    state = registry.Iot.State.DesiredRelay.get_device_state(
        burner.code,
        date=datetime(2020, 6 ,15, 11, 14)
    )
    assert state.is_open is False
    state = registry.Iot.State.DesiredRelay.get_device_state(
        burner.code,
        date=datetime(2020, 6 ,15, 11, 12)
    )
    assert state.is_open is True

def test_engine_desired_state(rollback_registry, burner, engine):
    State = rollback_registry.Iot.State
    state = State.DesiredRelay.get_device_state(
        engine.code,
        date=datetime(2020, 6 ,15, 11, 14)
    )
    assert state.is_open is True
    State.Relay.insert(device=burner, is_open=True, create_date=datetime(2020, 6, 15, 11, 10))
    state = State.DesiredRelay.get_device_state(
        engine.code,
        date=datetime(2020, 6 ,15, 11, 14)
    )
    assert state.is_open is True
    State.Relay.insert(device=burner, is_open=False, create_date=datetime(2020, 6, 15, 11, 10))
    state = State.DesiredRelay.get_device_state(
        engine.code,
        date=datetime(2020, 6 ,15, 11, 14)
    )
    assert state.is_open is False
    state = State.DesiredRelay.get_device_state(
        engine.code,
        date=datetime(2020, 6 ,15, 11, 9)
    )
    assert state.is_open is True
    state = State.DesiredRelay.get_device_state(
        engine.code,
        date=datetime(2020, 6 ,15, 13, 11)
    )
    assert state.is_open is True
    
