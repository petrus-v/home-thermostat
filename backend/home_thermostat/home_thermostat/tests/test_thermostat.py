from datetime import datetime, time, timedelta
from decimal import Decimal as D

import pytest

from home_thermostat.home_thermostat.common import ThermostatMode as Mode


@pytest.fixture(autouse=True)
def thermostat_mode(rollback_registry):
    rollback_registry.System.Parameter.set("mode", Mode.thermostat.value)

@pytest.fixture()
def advanced_settings(
    rollback_registry,
    max_depart_desired_temp,
    max_return_desired_temp,
    min_return_desired_temp,
    min_diff_living_depart_desired_temp,
):
    registry = rollback_registry
    Thermometer = registry.Iot.State.Thermometer
    Thermometer.insert(
        device=max_depart_desired_temp, create_date=datetime(2020, 6, 10, 10, 00), celsius=D("65")
    )
    Thermometer.insert(
        device=max_return_desired_temp, create_date=datetime(2020, 6, 10, 10, 00), celsius=D("45")
    )
    Thermometer.insert(
        device=min_return_desired_temp, create_date=datetime(2020, 6, 10, 10, 00), celsius=D("33")
    )
    Thermometer.insert(
        device=min_diff_living_depart_desired_temp, create_date=datetime(2020, 6, 10, 10, 00), celsius=D("5")
    )



@pytest.fixture()
def default_range(rollback_registry):
    Range = rollback_registry.Iot.Thermostat.Range
    Range.insert(
        create_date=datetime(2020, 6, 14),
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
    assert Range.get_desired_living_room_temperature(datetime(2020, 6, 14, 1)) == D(
        "15"
    )
    assert Range.get_desired_living_room_temperature(
        datetime(2020, 6, 16, 11, 14)
    ) == D("666")
    assert Range.get_desired_living_room_temperature(
        datetime(2020, 6, 16, 11, 12)
    ) == D("18.5")
    assert Range.get_desired_living_room_temperature(
        datetime(2020, 6, 15, 11, 14)
    ) == D("19")
    assert Range.get_desired_living_room_temperature(
        datetime(2020, 6, 15, 11, 12)
    ) == D("18.5")


@pytest.fixture()
def living_room_sensor_data(rollback_registry, living_room):
    registry = rollback_registry
    Thermometer = registry.Iot.State.Thermometer
    Thermometer.insert(
        device=living_room, create_date=datetime(2020, 6, 15, 10, 00), celsius=D("8.0")
    )
    Thermometer.insert(
        device=living_room, create_date=datetime(2020, 6, 15, 11, 00), celsius=D("18.0")
    )
    Thermometer.insert(
        device=living_room, create_date=datetime(2020, 6, 15, 11, 8), celsius=D("20.0")
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


def test_engine_desired_state(rollback_registry, burner, engine):
    State = rollback_registry.Iot.State
    state = State.DesiredRelay.get_device_state(
        engine.code, date=datetime(2020, 6, 15, 11, 14)
    )
    assert state.is_open is True
    State.Relay.insert(
        device=burner, is_open=True, create_date=datetime(2020, 6, 15, 11, 10)
    )
    state = State.DesiredRelay.get_device_state(
        engine.code, date=datetime(2020, 6, 15, 11, 14)
    )
    assert state.is_open is True
    State.Relay.insert(
        device=burner, is_open=False, create_date=datetime(2020, 6, 15, 11, 10)
    )
    state = State.DesiredRelay.get_device_state(
        engine.code, date=datetime(2020, 6, 15, 11, 14)
    )
    assert state.is_open is False
    state = State.DesiredRelay.get_device_state(
        engine.code, date=datetime(2020, 6, 15, 11, 9)
    )
    assert state.is_open is True
    state = State.DesiredRelay.get_device_state(
        engine.code, date=datetime(2020, 6, 15, 13, 11)
    )
    assert state.is_open is True


def test_thermostat_relay_and_engine_states(
    rollback_registry,
    default_range,
    advanced_settings,
    burner,
    living_room,
    engine,
    water_departures,
    water_returns,
):
    registry = rollback_registry
    Thermometer = registry.Iot.State.Thermometer
    State = rollback_registry.Iot.State
    clock = datetime(2020, 6, 15, 10, 00)

    def next_check(
        living_room_t=None,
        water_departures_t=None,
        water_returns_t=None,
        desired_burner_state_expected=None,
        desired_engine1_state_expected=None,
        desired_engine2_state_expected=None,
        desired_engine_later_state_expected=None,
    ):
        nonlocal clock
        # add 6 minutes to avoid headheak with averages
        clock += timedelta(minutes=6)
        Thermometer.insert(
            device=living_room, create_date=clock, celsius=living_room_t
        )
        Thermometer.insert(
            device=water_departures, create_date=clock, celsius=water_departures_t
        )
        Thermometer.insert(
            device=water_returns, create_date=clock, celsius=water_returns_t
        )
        clock += timedelta(minutes=1)
        desired_burner_state = State.DesiredRelay.get_device_state(
            burner.code, date=clock
        )
        assert desired_burner_state.is_open is desired_burner_state_expected
        desired_engine_state = State.DesiredRelay.get_device_state(
            engine.code, date=clock
        )
        assert desired_engine_state.is_open is desired_engine1_state_expected
        State.Relay.insert(
            device=burner, is_open=desired_burner_state_expected, create_date=clock
        )
        clock += timedelta(minutes=1)
        desired_engine_state = State.DesiredRelay.get_device_state(
            engine.code, date=clock
        )
        assert desired_engine_state.is_open is desired_engine2_state_expected
        State.Relay.insert(
            device=engine, is_open=desired_engine2_state_expected, create_date=clock
        )
        clock += timedelta(minutes=1)
        Thermometer.insert(
            device=living_room, create_date=clock + timedelta(hours=15), celsius=living_room_t
        )
        desired_engine_state = State.DesiredRelay.get_device_state(
            engine.code, date=clock + timedelta(hours=15)
        )
        assert desired_engine_state.is_open is desired_engine_later_state_expected

    # on démarre la chaudière
    next_check(
        living_room_t=D("8.0"),
        water_departures_t=D("4.0"),
        water_returns_t=D("4.0"),
        desired_burner_state_expected=False,
        desired_engine1_state_expected=True,
        desired_engine2_state_expected=False,
        desired_engine_later_state_expected=True,
    )
    # arret bruleur la température de départ est supériore à 65
    next_check(
        living_room_t=D("8.1"),
        water_departures_t=D("66.0"),
        water_returns_t=D("9.0"),
        desired_burner_state_expected=True,
        desired_engine1_state_expected=False,
        desired_engine2_state_expected=False,
        desired_engine_later_state_expected=True,
    )
    # la température est toujours en dessous on rallume le bruleur
    next_check(
        living_room_t=D("9.1"),
        water_departures_t=D("50.0"),
        water_returns_t=D("30.0"),
        desired_burner_state_expected=False,
        desired_engine1_state_expected=False,
        desired_engine2_state_expected=False,
        desired_engine_later_state_expected=False,
    )
    # de nouveau la température est trop chaud au départ
    next_check(
        living_room_t=D("10.0"),
        water_departures_t=D("66.0"),
        water_returns_t=D("35.0"),
        desired_burner_state_expected=True,
        desired_engine1_state_expected=False,
        desired_engine2_state_expected=False,
        desired_engine_later_state_expected=False,
    )
    # on a pas atteint le retour max on continue la chauffe
    next_check(
        living_room_t=D("10.1"),
        water_departures_t=D("40.0"),
        water_returns_t=D("40.0"),
        desired_burner_state_expected=False,
        desired_engine1_state_expected=False,
        desired_engine2_state_expected=False,
        desired_engine_later_state_expected=False,
    )
    # on a atteint le retour max
    next_check(
        living_room_t=D("10.2"),
        water_departures_t=D("47.0"),
        water_returns_t=D("46.0"),
        desired_burner_state_expected=True,
        desired_engine1_state_expected=False,
        desired_engine2_state_expected=False,
        desired_engine_later_state_expected=False,
    )
    # il faut attendre le retour min avant de chauffer de nouveau
    next_check(
        living_room_t=D("10.3"),
        water_departures_t=D("37.0"),
        water_returns_t=D("37.0"),
        desired_burner_state_expected=True,
        desired_engine1_state_expected=False,
        desired_engine2_state_expected=False,
        desired_engine_later_state_expected=False,
    )
    # on peut chauffer à nouveau le min désiré est atteint
    next_check(
        living_room_t=D("10.4"),
        water_departures_t=D("36.0"),
        water_returns_t=D("30.0"),
        desired_burner_state_expected=False,
        desired_engine1_state_expected=False,
        desired_engine2_state_expected=False,
        desired_engine_later_state_expected=False,
    )
    # départ trop chaud
    next_check(
        living_room_t=D("10.5"),
        water_departures_t=D("66.0"),
        water_returns_t=D("35.0"),
        desired_burner_state_expected=True,
        desired_engine1_state_expected=False,
        desired_engine2_state_expected=False,
        desired_engine_later_state_expected=False,
    )
    # keep going
    next_check(
        living_room_t=D("13.0"),
        water_departures_t=D("60.0"),
        water_returns_t=D("40.0"),
        desired_burner_state_expected=False,
        desired_engine1_state_expected=False,
        desired_engine2_state_expected=False,
        desired_engine_later_state_expected=False,
    )
    # température salon acceptable
    next_check(
        living_room_t=D("15.5"),
        water_departures_t=D("41.0"),
        water_returns_t=D("41.0"),
        desired_burner_state_expected=True,
        desired_engine1_state_expected=False,
        desired_engine2_state_expected=False,
        desired_engine_later_state_expected=False,
    )
    # température salon acceptable
    next_check(
        living_room_t=D("15.2"),
        water_departures_t=D("40.0"),
        water_returns_t=D("40.0"),
        desired_burner_state_expected=True,
        desired_engine1_state_expected=False,
        desired_engine2_state_expected=False,
        desired_engine_later_state_expected=False,
    )
    # la température est de nouveau sous la barre 
    # => on chauffe on avait pas atteint le max
    next_check(
        living_room_t=D("14.9"),
        water_departures_t=D("40.0"),
        water_returns_t=D("40.0"),
        desired_burner_state_expected=False,
        desired_engine1_state_expected=False,
        desired_engine2_state_expected=False,
        desired_engine_later_state_expected=False,
    )
    # la température de retour trop chaud
    next_check(
        living_room_t=D("14.8"),
        water_departures_t=D("47.0"),
        water_returns_t=D("46.0"),
        desired_burner_state_expected=True,
        desired_engine1_state_expected=False,
        desired_engine2_state_expected=False,
        desired_engine_later_state_expected=False,
    )
    # temp salon impecable
    next_check(
        living_room_t=D("15.8"),
        water_departures_t=D("38.0"),
        water_returns_t=D("37.0"),
        desired_burner_state_expected=True,
        desired_engine1_state_expected=False,
        desired_engine2_state_expected=False,
        desired_engine_later_state_expected=False,
    )
    # revient temperature de salon trop petite
    # mais on est pas encore redesendu sous le min
    next_check(
        living_room_t=D("14.9"),
        water_departures_t=D("37.0"),
        water_returns_t=D("34.0"),
        desired_burner_state_expected=True,
        desired_engine1_state_expected=False,
        desired_engine2_state_expected=False,
        desired_engine_later_state_expected=False,
    )
    # on peut chauffer de nouveau
    next_check(
        living_room_t=D("14.9"),
        water_departures_t=D("37.0"),
        water_returns_t=D("32.0"),
        desired_burner_state_expected=False,
        desired_engine1_state_expected=False,
        desired_engine2_state_expected=False,
        desired_engine_later_state_expected=False,
    )
    # il fait sufisament chaud dans la piece depuis un bout de temps
    # la température est redescendu
    next_check(
        living_room_t=D("15.8"),
        water_departures_t=D("15.0"),
        water_returns_t=D("15.0"),
        desired_burner_state_expected=True,
        desired_engine1_state_expected=False,
        desired_engine2_state_expected=False,
        desired_engine_later_state_expected=True,
    )
