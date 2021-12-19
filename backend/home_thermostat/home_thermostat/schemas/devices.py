import aprslib
from datetime import datetime, time
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel

from home_thermostat.home_thermostat.common import ThermostatMode as Mode


class ThermostatMode(BaseModel):
    mode: Mode = Mode.thermostat


class ThermostatRange(BaseModel):
    start: time = time(hour=0, minute=0)
    end: time = time(hour=23, minute=59)
    celsius: Decimal = Decimal("18.5")

    class Config:
        orm_mode = True


class Device(BaseModel):
    code: str = None
    name: str = None

    class Config:
        orm_mode = True


class BaseState(BaseModel):
    """based class used for typing purpose"""

    device: Device = None
    create_date: Optional[datetime] = None

    class Config:
        orm_mode = True


class RelayState(BaseState):
    is_open: bool = True
    """Tell whatever the network is open (turned off) or closed (turned off)
    """

    def __eq__(self, other: "RelayState") -> bool:
        return self.is_open == other.is_open


class ThermometerState(BaseState):

    celsius: Decimal = None


class FuelGaugeState(BaseState):

    level: int = None
    """Millimeter collected fioul level"""

class WeatherStationState(BaseState):
    """Weather state from APRS-IS packet"""

    # station_id: Optional[str] = None
    sensor_date: datetime = None
    wind_direction: Decimal = None
    wind_speed: Decimal = None
    wind_gust: Decimal = None
    temperature: Decimal = None
    rain_1h: Decimal = None
    rain_24h: Decimal = None
    rain_since_midnight: Decimal = None
    humidity: Decimal = None
    pressure: Decimal = None
    luminosity: Decimal = None

class APRSWeatherStationPacket(BaseModel):
    """APRS-IS raw data"""

    raw: str = None
    code: Optional[str] = None

    def parse(self) -> WeatherStationState:
        data: dict = aprslib.parse(self.raw)
        self.code = data["from"]
        return WeatherStationState(
            sensor_date=datetime.fromtimestamp(data["timestamp"]),
            **data["weather"]
        )
