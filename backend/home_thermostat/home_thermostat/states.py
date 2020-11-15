from datetime import datetime, time, timedelta
from decimal import Decimal as D
from logging import getLogger
from uuid import uuid4

from anyblok import Declarations
from anyblok.column import UUID, Boolean, Decimal, Integer, Selection, String, Time
from anyblok.field import Function
from anyblok.relationship import Many2One
from anyblok_postgres.column import Jsonb
from sqlalchemy.sql import func

from .common import ThermostatMode

logger = getLogger(__name__)
Model = Declarations.Model
Mixin = Declarations.Mixin

from typing import Any, Optional, Type, Union


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

    @classmethod
    def get_desired_living_room_temperature(cls, date: datetime) -> Optional[D]:
        if not date:
            date = datetime.now()
        range_ = (
            cls.query()
            .distinct(cls.code)
            .filter(cls.start <= date.time(), cls.end > date.time())
            .filter(cls.create_date < date)
            .order_by(cls.code.desc())
            .order_by(cls.create_date.desc())
            .first()
        )
        if range_:
            return range_.celsius
        return None


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

    @classmethod
    def get_device_state(
        cls,
        code: str,
    ) -> Union[
        "registry.Iot.State.Relay",
        "registry.Iot.State.DesiredRelay",
        "registry.Iot.State.Thermometer",
        "registry.Iot.State.FuelGauge",
    ]:
        """Cast states.State -> DeviceState is done throught fastAPI"""
        Device = cls.registry.Iot.Device
        state = (
            cls.query()
            .join(Device)
            .filter(Device.code == code)
            .order_by(cls.registry.Iot.State.create_date.desc())
            .first()
        )
        if not state:
            device = Device.query().filter_by(code=code).one()
            # We don't want to instert a new state here, just creating
            # a default instance
            state = cls(device=device)
            cls.registry.flush()
        return state


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

    @classmethod
    def get_device_state(cls, code: str, date: datetime = None) -> "DesiredRelay":
        """return desired state for given device code"""
        mode = ThermostatMode(
            cls.registry.System.Parameter.get("mode", default="manual")
        )
        if mode is ThermostatMode.manual:
            return super().get_device_state(code)
        else:
            if not date:
                date = datetime.now()
            return {
                "BURNER": cls.get_burner_thermostat_desired_state,
                "ENGINE": cls.get_engine_thermostat_desired_state,
            }[code](date)

    @classmethod
    def get_burner_thermostat_desired_state(cls, date: datetime) -> "DesiredRelay":
        Thermometer = cls.registry.Iot.State.Thermometer
        Range = cls.registry.Iot.Thermostat.Range
        celsius_avg = Thermometer.get_living_room_avg(date=date)
        if not celsius_avg:
            return cls(is_open=True)
        celsius_desired = Range.get_desired_living_room_temperature(date)
        if celsius_avg <= celsius_desired:
            return cls(is_open=False)
        return cls(is_open=True)

    @classmethod
    def get_engine_thermostat_desired_state(
        cls, date: datetime, delta_minutes=120
    ) -> "DesiredRelay":
        """If burner relay was on in last delta_minutes, engine must turn on"""
        Relay = cls.registry.Iot.State.Relay
        Device = cls.registry.Iot.Device
        count_states = (
            Relay.query()
            .join(Device)
            .filter(
                Relay.create_date > date - timedelta(minutes=delta_minutes),
                Relay.create_date <= date,
                Device.code == "BURNER",
                Relay.is_open == False,
            )
        )
        return cls(is_open=count_states.count() == 0)


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

    @classmethod
    def get_living_room_avg(cls, date: datetime, minutes: int = 15):
        if not date:
            date = datetime.now()

        Device = cls.registry.Iot.Device
        # query = Thermometer.query(func.avg(Thermometer.celsius).label('average')).join(Device).filter(Device.code == "28-01193a44fa4c").filter(cls.registry.Iot.State.create_date >= date - timedelta(minutes=15)).group_by(Device.code)
        return (
            cls.query(func.avg(cls.celsius).label("average"))
            .join(Device)
            .filter(Device.code == "28-01193a44fa4c")  # Salon
            .filter(
                cls.create_date > date - timedelta(minutes=minutes),
                cls.create_date <= date,
            )
            .group_by(Device.code)
            .scalar()
        )


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
