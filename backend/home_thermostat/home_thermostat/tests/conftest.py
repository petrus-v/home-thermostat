from anyblok.conftest import *  # noqa: F401,F403
from anyblok_fastapi.conftest import webserver  # noqa: F401


@pytest.fixture
def burner(rollback_registry):
    return get_device(rollback_registry, "burner")


@pytest.fixture
def engine(rollback_registry):
    return get_device(rollback_registry, "engine")


def get_device(registry, external_id):
    return registry.IO.Mapping.get(
        "Model.IOT.Device", external_id
    )