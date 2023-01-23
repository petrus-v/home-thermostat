import pigpio
import argparse
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


@dataclass
class ThermometerSensor:

    pi: pigpio.pi = None
    """pigpio deamon connection"""

    def read(self) -> Dict[str, float]:
        results = {}
        _, files = self.pi.file_list("/sys/bus/w1/devices/28-*/w1_slave")

        for sensor in files.decode().strip().split("\n"):

            """
            Typical file name

            /sys/bus/w1/devices/28-000005d34cd2/w1_slave
            """

            device_id = sensor.split("/")[5]  # Fifth field is the device Id.

            h = self.pi.file_open(sensor, pigpio.FILE_READ)
            data = self.pi.file_read(h, 1000)[1].decode()  # 1000 is plenty to read full file.
            self.pi.file_close(h)

            """
            Typical file contents

            73 01 4b 46 7f ff 0d 10 41 : crc=41 YES
            73 01 4b 46 7f ff 0d 10 41 t=23187
            """

            if "YES" in data:
                (_, _, reading) = data.partition(' t=')
                results[device_id] = float(reading) / 1000.0
        return results

def common_settings(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        '--base-url',
        dest="base_url",
        default=DEFAULT_BASE_URL,
        help=f"Base url {DEFAULT_BASE_URL}",
    )
    parser.add_argument(
        '--print-only',
        "-p",
        dest="print_only",
        action="store_true",
        help=f"Do not send data, only print results",
    )
    # parser.add_argument(
    #     "devices",
    #     metavar='D',
    #     type=str,
    #     nargs='+',
    #     help=f"Thermometer sensors serial addresses "
    #          f"(ls -d /sys/bus/w1/devices/28-*)",
    # )


def read():
    parser = argparse.ArgumentParser(
        description="""Read temperature sensors and send state

        This is used by thermometer sensor
        getting card settings instructions from https://github.com/timofurrer/w1thermsensor
        Raspi VCC (3V3) Pin 1 -- red -------- red -------   VCC    DS18B20
                                                            |
                                                            |
                                                            R1 = 4k7 ...10k
                                                            |
                                                            |
        Raspi GPIO 4    Pin 7 -- yellow ----- yellow ----   Data   DS18B20


        Raspi GND       Pin 6 -- orange ----- black -----   GND    DS18B20

        """
    )
    common_settings(parser)
    args = parser.parse_args()

    with pigpio_client() as pi:
        devices_states = ThermometerSensor(pi=pi).read()
    if args.print_only:
        print(devices_states)
        return

    for device, state in devices_states.items():
        url: str = urljoin(args.base_url, f"thermometer/{device}/state")
        r = requests.post(
            url,
            json={"celsius": state},
            auth=HTTPBasicAuth(LOGIN, PASSWORD),
        )
        if r.status_code != 200:
            raise RuntimeError(
                f"Got following error while posting data: data to {url}: "
                f"{r}"
            )
