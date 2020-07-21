"""Blok declaration example
"""
from typing import TYPE_CHECKING, Callable, List

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
    required = [
        "anyblok-core",
        "anyblok-mixins",
        "anyblok-io-xml"
    ]

    @classmethod
    def import_declaration_module(cls) -> None:
        """Python module to import in the given order at start-up"""
        from . import states  # noqa
        from .schemas import relay  # noqa


    @classmethod
    def reload_declaration_module(
        cls, reload: "Callable[[ModuleType], None]"
    ) -> None:
        """Python module to import while reloading server (ie when
        adding Blok at runtime
        """
        from . import states  # noqa
        from .schemas import relay  # noqa

        reload(states)


    def update(self, latest: "AnyBlokVersion") -> None:
        """Update blok"""
        self.import_file_xml(
            "Model.IOT.Device", "data", "iot.device.xml"
        )


    def load(self) -> None:
        from .api import (
            device_state,
            save_device_state,
            device_desired_state,
            save_device_desired_state,
        )
        from .schemas.relay import RelayState

        self.registry.declare_routes(
            {
                "GET/api/device/{code}/state": APIRoute(
                    "/api/device/{code}/state",
                    device_state,
                    methods=["GET"],
                    response_class=JSONResponse,
                ),
                "POST/api/device/{code}/state": APIRoute(
                    "/api/device/{code}/state",
                    save_device_state,
                    methods=["POST"],
                    response_class=JSONResponse,
                ),
                "GET/api/device/{code}/desired/state": APIRoute(
                    "/api/device/{code}/desired/state",
                    device_desired_state,
                    methods=["GET"],
                    response_class=JSONResponse,
                ),
                "POST/api/device/{code}/desired/state": APIRoute(
                    "/api/device/{code}/desired/state",
                    save_device_desired_state,
                    methods=["POST"],
                    response_class=JSONResponse,
                ),
            }
        )
