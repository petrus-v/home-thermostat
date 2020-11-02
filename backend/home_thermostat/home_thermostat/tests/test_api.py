import pytest
import respx
from anyblok_fastapi.conftest import webserver  # noqa: F401
from home_thermostat.home_thermostat.schemas.relay import RelayState 
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound


@pytest.fixture
def some_states(rollback_registry, engine):
    generate_states(rollback_registry.IOT.State, engine)


@pytest.fixture
def some_desired_states(rollback_registry, engine):
    generate_states(rollback_registry.IOT.DesiredState, engine)


def generate_states(State, engine):
    State.insert(
        device=engine,
        state=RelayState(is_open=True).json(),
        create_date=datetime(2020, 6, 15, 9, 42)
    )
    State.insert(
        device=engine,
        state=RelayState(is_open=False).json(),
        create_date=datetime(2020, 6, 15, 9, 55)
    )
    State.insert(
        device=engine,
        state=RelayState(is_open=True).json(),
        create_date=datetime(2020, 6, 15, 10, 42)
    )
    State.insert(
        device=engine,
        state=RelayState(is_open=False).json(),
        create_date=datetime(2020, 6, 15, 11, 42)
    )


def test_api_device_code_state_get_latest_state(
    rollback_registry, webserver, engine, some_states
):
    response = webserver.get(f"/api/device/{engine.code}/state")
    assert response.status_code == 200
    assert response.json() == {
        "is_open": False
    }


def test_api_device_code_state_get_latest_state_not_defined(
    rollback_registry, webserver, engine
):
    response = webserver.get(f"/api/device/{engine.code}/state")
    assert response.status_code == 200
    assert response.json() == {
        "is_open": True
    }


def test_api_device_code_state_wrong_code(
    rollback_registry, webserver, some_states
):
    with pytest.raises(NoResultFound):
        response = webserver.get(f"/api/device/UNKNOWN/state")


def test_save_device_state(
    rollback_registry, webserver, engine
):
    registry = rollback_registry
    State = registry.IOT.State
    count_before = State.query().count()
    response = webserver.post(f"/api/device/{engine.code}/state", data='{"is_open": true}')
    assert response.status_code == 200, str(response)
    assert count_before + 1 == State.query().count()



def test_save_device_state_unkwon_device(
    rollback_registry, webserver
):
    registry = rollback_registry
    State = registry.IOT.State
    count_before = State.query().count()
    with pytest.raises(NoResultFound):
        webserver.post(f"/api/device/UNKNOWN/state", data='{"is_open": true}')
    

def test_save_device_state_wrong_format(
    rollback_registry, webserver, engine
):
    registry = rollback_registry
    State = registry.IOT.State
    count_before = State.query().count()
    response = webserver.post(
        f"/api/device/{engine.code}/state",
        data='{"is_open": "wrong type", "extra": true}'
    )
    assert response.status_code == 422, str(response)
    assert count_before + 0 == State.query().count()




def test_api_device_code_desired_state_get_latest_state(
    rollback_registry, webserver, engine, some_desired_states
):
    response = webserver.get(f"/api/device/{engine.code}/desired/state")
    assert response.status_code == 200
    assert response.json() == {
        "is_open": False
    } 


def test_api_device_code_desired_state_get_latest_state_not_defined(
    rollback_registry, webserver, engine
):
    response = webserver.get(f"/api/device/{engine.code}/desired/state")
    assert response.status_code == 200
    assert response.json() == {
        "is_open": True
    }


def test_api_device_code_desired_state_wrong_code(
    rollback_registry, webserver, some_desired_states
):
    with pytest.raises(NoResultFound):
        response = webserver.get(f"/api/device/UNKNOWN/desired/state")


def test_save_device_desired_state(
    rollback_registry, webserver, engine
):
    registry = rollback_registry
    State = registry.IOT.DesiredState
    count_before = State.query().count()
    response = webserver.post(f"/api/device/{engine.code}/desired/state", data='{"is_open": true}')
    assert response.status_code == 200, str(response)
    assert count_before + 1 == State.query().count()



def test_save_device_desired_state_unkwon_device(
    rollback_registry, webserver, some_desired_states
):
    registry = rollback_registry
    State = registry.IOT.DesiredState
    count_before = State.query().count()
    with pytest.raises(NoResultFound):
        webserver.post(f"/api/device/UNKNOWN/desired/state", data='{"is_open": true}')
    

def test_save_device_desired_state_wrong_format(
    rollback_registry, webserver, engine
):
    registry = rollback_registry
    State = registry.IOT.DesiredState
    count_before = State.query().count()
    response = webserver.post(
        f"/api/device/{engine.code}/desired/state",
        data='{"is_open": "wrong type", "extra": true}'
    )
    assert response.status_code == 422, str(response)
    assert count_before + 0 == State.query().count()
    