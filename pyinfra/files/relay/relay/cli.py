import pigpio
import argparse
import json
import requests

from dataclasses import dataclass
from typing import Dict
from enum import Enum

from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin
from contextlib import contextmanager


DEFAULT_BASE_URL = os.environ["THERMOSTAT_BACKEND_URL"] + "/api/device/"
LOGIN = os.environ["THERMOSTAT_BACKEND_LOGIN"]
PASSWORD = os.environ["THERMOSTAT_BACKEND_PASSWORD"]



@contextmanager
def pigpio_client(*args, **kwrgs) -> pigpio.pi:
    """Open a connection to the pigpio deamon"""
    pi = pigpio.pi(*args, **kwrgs)

    if not pi.connected:
        raise RuntimeError("Could not etablish connection to the pigpio Deamon")
    try:
        yield pi
    finally:
        if pi.connected:
            pi.stop()


class RelayState(Enum):
    """Represent circuit OPEN means turned off, CLOSE means turned on"""

    OPEN = 1
    CLOSE = 0

    def to_dict(self) -> Dict[str, bool]:
        formated_state: Dict[str, bool]= {"is_open": False}
        if self is RelayState.OPEN:
            formated_state["is_open"] = True
        return formated_state

@dataclass
class Relay:

    pin: int = None
    """Pin Number"""

    pi: pigpio.pi = None
    """pigpio deamon connection"""

    def read(self) -> RelayState:
        return RelayState(self.pi.read(self.pin))

    def write(self, state: RelayState) -> None:
        self.pi.write(self.pin, state.value)


def common_settings(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        '--base-url',
        dest="base_url",
        default=DEFAULT_BASE_URL,
        help=f"Base url {DEFAULT_BASE_URL}",
    )
    parser.add_argument(
        'device',
        choices=["BURNER", "ENGINE"],
        help='Name of the device which is drived',
    )
    parser.add_argument(
        'pin',
        type=int,
        # choices=range(1, 28),  # from GPIO 1 to 27
        help="The GPIO pin number (ie: define 23 for GPIO 23 which is the 16th "
             "physical pin)",
    )

def write():
    parser = argparse.ArgumentParser(description='Retreive desired')
    common_settings(parser)
    args = parser.parse_args()
    url: str = urljoin(args.base_url, f"relay/{args.device}/desired/state")
    r = requests.get(
        url,
        auth=HTTPBasicAuth(LOGIN, PASSWORD),
    )
    if r.status_code != 200:
        raise RuntimeError(f"Got following error while retreiving {url}: {r}")
    desired_state = RelayState.OPEN if r.json()["is_open"] else RelayState.CLOSE

    with pigpio_client() as pi:
        Relay(pin=args.pin, pi=pi).write(desired_state)


def read():
    parser = argparse.ArgumentParser(
        description="Read relay device state and publish it"
    )
    common_settings(parser)
    args = parser.parse_args()

    with pigpio_client() as pi:
        current_state = Relay(pin=args.pin, pi=pi).read()

    url: str = urljoin(args.base_url, f"relay/{args.device}/state")
    r = requests.post(
        url,
        #TODO: try using righ json header instead json dumps things
        data=json.dumps(current_state.to_dict()),
        auth=HTTPBasicAuth(LOGIN, PASSWORD),
    )
    if r.status_code != 200:
        raise RuntimeError(
            f"Got following error while posting {current_state} "
            f"to {url}: {r}"
        )
