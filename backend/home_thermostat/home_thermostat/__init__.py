"""Blok declaration example
"""
from typing import TYPE_CHECKING, Callable, List, Union

from fastapi.routing import APIRoute
from starlette.responses import JSONResponse
from starlette.routing import Route
from anyblok_io.blok import BlokImporter
from anyblok.blok import Blok

if TYPE_CHECKING:
    from types import ModuleType
    from typing import Callable
    from anyblok.version import AnyBlokVersion


class HomeThermostat(Blok, BlokImporter):
    """Core_task's Blok class definition"""

    version = "0.1.0"
    author = "Pierre Verkest"
    required = ["anyblok-core", "anyblok-mixins", "anyblok-io-xml"]

    @classmethod
    def import_declaration_module(cls) -> None:
        """Python module to import in the given order at start-up"""
        from . import states  # noqa
        from .schemas import devices  # noqa

    @classmethod
    def reload_declaration_module(
        cls, reload: "Callable[[ModuleType], None]"
    ) -> None:
        """Python module to import while reloading server (ie when
        adding Blok at runtime
        """
        from . import states  # noqa
        from .schemas import devices  # noqa

        reload(states)

    def update(self, latest: "AnyBlokVersion") -> None:
        """Update blok"""
        self.import_file_xml("Model.Iot.Device", "data", "iot.device.xml")

    def load(self) -> None:
        from .api import (
            device_relay_state,
            device_fuel_gauge_state,
            device_thermometer_state,
            save_device_relay_state,
            save_device_fuel_gauge_state,
            save_device_thermometer_state,
            device_relay_desired_state,
            save_device_relay_desired_state,
        )
        from .schemas.devices import RelayState, ThermometerState, FuelGauge

        self.registry.declare_routes(
            {
                "GET/api/device/relay/{code}/state": APIRoute(
                    "/api/device/relay/{code}/state",
                    device_relay_state,
                    methods=["GET"],
                    response_class=JSONResponse,
                    response_model=RelayState,
                ),
                "POST/api/device/relay/{code}/state": APIRoute(
                    "/api/device/relay/{code}/state",
                    save_device_relay_state,
                    methods=["POST"],
                    response_class=JSONResponse,
                    response_model=RelayState,
                ),
                "GET/api/device/relay/{code}/desired/state": APIRoute(
                    "/api/device/relay/{code}/desired/state",
                    device_relay_desired_state,
                    methods=["GET"],
                    response_class=JSONResponse,
                    response_model=RelayState,
                ),
                "POST/api/device/relay/{code}/desired/state": APIRoute(
                    "/api/device/relay/{code}/desired/state",
                    save_device_relay_desired_state,
                    methods=["POST"],
                    response_class=JSONResponse,
                    response_model=RelayState,
                ),
                "GET/api/device/fuel-gauge/{code}/state": APIRoute(
                    "/api/device/fuel-gauge/{code}/state",
                    device_fuel_gauge_state,
                    methods=["GET"],
                    response_class=JSONResponse,
                    response_model=FuelGauge,
                ),
                "POST/api/device/fuel_gauge/{code}/state": APIRoute(
                    "/api/device/fuel_gauge/{code}/state",
                    save_device_fuel_gauge_state,
                    methods=["POST"],
                    response_class=JSONResponse,
                    response_model=FuelGauge,
                ),
                "GET/api/device/thermometer/{code}/state": APIRoute(
                    "/api/device/thermometer/{code}/state",
                    device_thermometer_state,
                    methods=["GET"],
                    response_class=JSONResponse,
                    response_model=ThermometerState,
                ),
                "POST/api/device/thermometer/{code}/state": APIRoute(
                    "/api/device/thermometer/{code}/state",
                    save_device_thermometer_state,
                    methods=["POST"],
                    response_class=JSONResponse,
                    response_model=ThermometerState,
                ),
            }
        )
