from anyblok.conftest import *  # noqa: F401,F403
from anyblok_fastapi.conftest import webserver  # noqa: F401


@pytest.fixture
def water_departures(rollback_registry):
    return get_device(rollback_registry, "temperature_sensor_28-01193a4a4aa2")


@pytest.fixture
def water_returns(rollback_registry):
    return get_device(rollback_registry, "temperature_sensor_28-01193a77449f")


@pytest.fixture
def living_room(rollback_registry):
    return get_device(rollback_registry, "temperature_sensor_28-01193a44fa4c")


@pytest.fixture
def fioul_gauge(rollback_registry):
    return get_device(rollback_registry, "fuel-gauge")


@pytest.fixture
def burner(rollback_registry):
    return get_device(rollback_registry, "burner")


@pytest.fixture
def engine(rollback_registry):
    return get_device(rollback_registry, "engine")


@pytest.fixture
def max_depart_desired_temp(rollback_registry):
    return get_device(rollback_registry, "max_depart_desired_temperature")


@pytest.fixture
def max_return_desired_temp(rollback_registry):
    return get_device(rollback_registry, "max_return_desired_temperature")


@pytest.fixture
def min_return_desired_temp(rollback_registry):
    return get_device(rollback_registry, "min_return_desired_temperature")


@pytest.fixture
def min_diff_living_depart_desired_temp(rollback_registry):
    return get_device(rollback_registry, "min_diff_living_depart_desired_temperature")


def get_device(registry, external_id):
    device = registry.IO.Mapping.get("Model.Iot.Device", external_id)
    if not device:
        raise RuntimeError(f"Device not found for given external id {external_id}")
    return device
