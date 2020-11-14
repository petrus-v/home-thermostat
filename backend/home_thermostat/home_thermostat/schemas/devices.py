from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from home_thermostat.home_thermostat.common import ThermostatMode as Mode


class ThermostatMode(BaseModel):
    mode: Mode = Mode.thermostat

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
