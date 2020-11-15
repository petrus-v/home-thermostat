from enum import Enum


class ThermostatMode(str, Enum):
    """Tell what's the current mode (manual/thermostat)"""

    manual = "manual"
    thermostat = "thermostat"
