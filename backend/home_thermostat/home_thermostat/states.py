from logging import getLogger
from decimal import Decimal as D
from datetime import time
from anyblok import Declarations
from anyblok.column import UUID, Boolean, Decimal, Integer, String, Selection, Time
from anyblok.relationship import Many2One
from anyblok.field import Function
from anyblok_postgres.column import Jsonb
from uuid import uuid4


logger = getLogger(__name__)
Model = Declarations.Model
Mixin = Declarations.Mixin

from typing import Any, Union, Type



@Declarations.register(Model)
class Iot:
    """Namespace for Iot"""


@Declarations.register(Model.Iot)
class Thermostat:
    """Namespace for Iot.Thermostat"""

@Declarations.register(Model.Iot.Thermostat)
class Range(Mixin.UuidColumn, Mixin.TrackModel):
    code: str = String(label="Code", index=True, nullable=False)
    start: time = Time(default=time(hour=0, minute=0))
    end: time = Time(default=time(hour=23, minute=59))
    celsius: D = Decimal(label="Thermometer (°C)")


@Declarations.register(Model.Iot)
class Device(Mixin.UuidColumn):
    name: str = String(label="Name", nullable=False)
    code: str = String(label="Code", unique=True, index=True, nullable=False)


@Declarations.register(Model.Iot)
class State(Mixin.UuidColumn, Mixin.TrackModel):

    STATE_TYPE = None

    device = Many2One(
        label="Devie",
        model=Declarations.Model.Iot.Device,
        one2many="states",
        nullable=False,
    )
    state_type = Selection(selections="get_device_types", nullable=False)

    @classmethod
    def define_mapper_args(cls):
        mapper_args = super().define_mapper_args()
        if cls.__registry_name__ == "Model.Iot.State":
            mapper_args.update({"polymorphic_on": cls.state_type})

        mapper_args.update({"polymorphic_identity": cls.STATE_TYPE})
        return mapper_args

    @classmethod
    def get_device_types(cls):
        return dict(
            DESIRED_RELAY="RelayDesired",
            RELAY="Relay",
            TEMPERATURE="Thermometer",
            FUEL_GAUGE="fuelgauge",
        )

    @classmethod
    def query(cls, *args, **kwargs):
        query = super().query(*args, **kwargs)
        if cls.__registry_name__.startswith("Model.Iot.State."):
            query = query.filter(cls.state_type == cls.STATE_TYPE)

        return query


@Declarations.register(Model.Iot.State)
class Relay(Model.Iot.State):

    STATE_TYPE = "RELAY"

    uuid: uuid4 = UUID(
        primary_key=True,
        default=uuid4,
        binary=False,
        foreign_key=Model.Iot.State.use("uuid").options(ondelete="CASCADE"),
    )
    is_open: bool = Boolean(label="Is open ?", default=True)
    """Current circuit state. is_open == True means circuit open, it's turned
    off"""


@Declarations.register(Model.Iot.State)
class DesiredRelay(Model.Iot.State):

    STATE_TYPE = "DESIRED_RELAY"

    uuid: uuid4 = UUID(
        primary_key=True,
        default=uuid4,
        binary=False,
        foreign_key=Model.Iot.State.use("uuid").options(ondelete="CASCADE"),
    )
    is_open: bool = Boolean(label="Is open ?", default=True)
    """Current circuit state. is_open == True means circuit open, it's turned
    off"""


@Declarations.register(Model.Iot.State)
class Thermometer(Model.Iot.State):

    STATE_TYPE = "TEMPERATURE"

    uuid: uuid4 = UUID(
        primary_key=True,
        default=uuid4,
        binary=False,
        foreign_key=Model.Iot.State.use("uuid").options(ondelete="CASCADE"),
    )

    celsius: D = Decimal(label="Thermometer (°C)")


@Declarations.register(Model.Iot.State)
class FuelGauge(Model.Iot.State):

    STATE_TYPE = "FUEL_GAUGE"

    uuid: uuid4 = UUID(
        primary_key=True,
        default=uuid4,
        binary=False,
        foreign_key=Model.Iot.State.use("uuid").options(ondelete="CASCADE"),
    )
    level: int = Integer(label="Fuel level (mm)")
