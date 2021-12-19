from datetime import datetime, time, timedelta
from decimal import Decimal as D
from enum import Enum
from logging import getLogger
from typing import Optional, Union
from uuid import uuid4

from anyblok import Declarations, registry
from anyblok.column import UUID, Boolean, DateTime, Decimal, Integer, Selection, String, Time
from anyblok.relationship import Many2One
from sqlalchemy.sql import func

from .common import ThermostatMode

logger = getLogger(__name__)
Model = Declarations.Model
Mixin = Declarations.Mixin

class DEVICE(Enum):
    ENGINE = "ENGINE"
    BURNER_RELAY = "BURNER"

    FUEL_GAUGE = "FUEL"
    WEATHER_STATION = "WEATHER"
    
    LIVING_ROOM_SENSOR = "28-01193a44fa4c"
    DEPARTURE_SENSOR = "28-01193a4a4aa2"
    RETURN_SENOR = "28-01193a77449f"
    UNSUSED_SENSOR = "28-01193a490806"
    OUTSIDE_SENSOR = "28-01193a503a1a"

    MAX_DEP_DESIRED = "max-depart"
    MAX_RET_DESIRED = "max-return"
    MIN_RET_DESIRED = "min-return"
    MIN_DIFF_DESIRED = "min-diff-engine"


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
        subquery = (
            cls.query()
            .distinct(cls.code)
            .filter(cls.create_date < date)
            .order_by(cls.code.desc())
            .order_by(cls.create_date.desc())
            .subquery()
        )
        range_ = (
            cls.registry.query(subquery.c.celsius)
            .select_from(subquery)
            .filter(subquery.c.start <= date.time(), subquery.c.end > date.time())
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
            WEATHER_STATION="WeatherStation",
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
        "registry.Model.Iot.State.Relay",
        "registry.Model.Iot.State.DesiredRelay",
        "registry.Model.Iot.State.Thermometer",
        "registry.Model.Iot.State.FuelGauge",
        "registry.Model.Iot.State.WeatherStation",
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
        celsius_avg = Thermometer.get_living_room_avg(date=date, minutes=5)
        if not celsius_avg:
            # there are no thermometer working
            # user should move to manual mode
            return cls(is_open=True)
        if Thermometer.wait_min_return_desired_temperature(
            DEVICE.DEPARTURE_SENSOR,
            DEVICE.MIN_RET_DESIRED,
            DEVICE.MAX_DEP_DESIRED,
        ):
            # departure is to hot or waiting under ret min desired
            return cls(is_open=True)
        celsius_desired = Range.get_desired_living_room_temperature(date)
        if celsius_avg >= celsius_desired:
            # living room is already warm
            return cls(is_open=True)
        if Thermometer.get_last_value(DEVICE.RETURN_SENOR.value) >= Thermometer.get_last_value(DEVICE.MAX_RET_DESIRED.value):
            # return temperature is to hot
            return cls(is_open=True)
        if Thermometer.wait_min_return_desired_temperature(
            DEVICE.RETURN_SENOR,
            DEVICE.MIN_RET_DESIRED,
            DEVICE.MAX_RET_DESIRED,
        ):
            # wait return temperature to get the DEVICE.MIN_RET_DESIRED.value
            # temperature before start burner again
            return cls(is_open=True)
        return cls(is_open=False)

    @classmethod
    def get_engine_thermostat_desired_state(
        cls, date: datetime, delta_minutes=120
    ) -> "DesiredRelay":
        """
        If 
          burner relay was on in last delta_minutes,
          or if return water - living room is more than diff config value
        then engine must be turned on
        """
        Thermometer = cls.registry.Iot.State.Thermometer
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
        living_room_avg_temp = Thermometer.get_living_room_avg(date=date, minutes=5)
        return_temp = Thermometer.get_last_value(DEVICE.RETURN_SENOR.value)
        min_diff = Thermometer.get_last_value(DEVICE.MIN_DIFF_DESIRED.value)
        return cls(is_open=not (
            (count_states.count() > 0)
            or (return_temp - living_room_avg_temp > min_diff)
        ))


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
    def get_last_value(cls, device_code: str):
        Device = cls.registry.Iot.Device
        last = (
            cls.query()
            .join(Device)
            .filter(Device.code == device_code)
            .order_by(cls.registry.Iot.State.create_date.desc())
            .first()
        )
        if last:
            return last.celsius
        return 0
    
    @classmethod
    def wait_min_return_desired_temperature(cls, device_sensor: DEVICE, device_min: DEVICE, device_max: DEVICE):
        # wait return temperature to get the DEVICE.MIN_RET_DESIRED.value
        # temperature before start burner again
        Device = cls.registry.Iot.Device
        State = cls.registry.Iot.State
        min_temp = cls.get_last_value(device_min.value)
        max_temp = cls.get_last_value(device_max.value)
        last_pick = (
            cls.query()
            .join(Device)
            .filter(Device.code == device_sensor.value)
            .filter(cls.celsius >= max_temp)
            .order_by(State.create_date.desc())
            .first()
        )
        if not last_pick:
            return False
        last_curve = (
            cls.query()
            .join(Device)
            .filter(Device.code == device_sensor.value)
            .filter(cls.celsius <= min_temp)
            .filter(State.create_date > last_pick.create_date)
            .order_by(State.create_date.desc())
            .first()
        )
        if not last_curve:
            return True
        return False

    @classmethod
    def get_living_room_avg(cls, date: datetime = None, minutes=5):
        avg = cls.get_sensor_avg(DEVICE.LIVING_ROOM_SENSOR.value, date=date, minutes=minutes)
        if not avg:
            return 0
        return  avg

    @classmethod
    def get_sensor_avg(cls, device_code: str, date: datetime = None, minutes: int = 15):
        if not date:
            date = datetime.now()
        Device = cls.registry.Iot.Device
        return (
            cls.query(func.avg(cls.celsius).label("average"))
            .join(Device)
            .filter(Device.code == device_code)
            .filter(
                cls.create_date > date - timedelta(minutes=minutes),
                cls.create_date <= date,
            )
            .group_by(Device.code)
            .scalar()
        )



@Declarations.register(Model.Iot.State)
class WeatherStation(Model.Iot.State):
    """Weather state from APRS-IS packet"""

    STATE_TYPE = "WEATHER_STATION"

    uuid: uuid4 = UUID(
        primary_key=True,
        default=uuid4,
        binary=False,
        foreign_key=Model.Iot.State.use("uuid").options(ondelete="CASCADE"),
    )
    sensor_date: DateTime = DateTime(
        label="Sensor timestamp",
        primary_key=True,
    )
    wind_direction: D = Decimal(label="Wind direction")
    wind_speed: D = Decimal(label="Wind Speed (km/h ?)")
    wind_gust: D = Decimal(label="Wind gust (km/h ?)")
    temperature: D = Decimal(label="Thermometer (°C)")
    rain_1h: D = Decimal(label="rain (mm/1h)")
    rain_24h: D = Decimal(label="rain (mm/24h)")
    rain_since_midnight: D = Decimal(label="rain (mm/since midnight)")
    humidity: D = Decimal(label="Humidity (%)")
    pressure: D = Decimal(label="Pressure (hPa)")
    luminosity: D = Decimal(label="Luminosity/irradiation (W/m2)")
    

    @classmethod
    def get_last_state(cls, device_code: str):
        """this method is different from get_device_state because
        it do not use the same field to order values"""
        Device = cls.registry.Iot.Device
        return (
            cls.query()
            .join(Device)
            .filter(Device.code == device_code)
            .order_by(cls.sensor_date.desc())
            .first()
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
