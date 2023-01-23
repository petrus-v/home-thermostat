import argparse
import requests
import aprslib

from requests.auth import HTTPBasicAuth
from urllib.parse import urljoin

DEFAULT_BASE_URL = os.environ["THERMOSTAT_BACKEND_URL"] + "/api/device/"
LOGIN = os.environ["THERMOSTAT_BACKEND_LOGIN"]
PASSWORD = os.environ["THERMOSTAT_BACKEND_PASSWORD"]

APRS_CALLSIGN = os.environ.get("THERMOSTAT_APRS_CALLSIGN", "GW0973")
DEVICE = os.environ.get("THERMOSTAT_APRS_FOLLOWED_STATION", "FW5282")


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
    parser.add_argument(
        "--call-sign",
        "-c",
        dest="callsign",
        default=APRS_CALLSIGN,
        type=str,
        help=f"Server to listen",
    )
    parser.add_argument(
        "--station",
        "-s",
        dest="station",
        default=APRS_FOLLOWED_STATION,
        type=str,
        help=f"Server to listen",
    )
    parser.add_argument(
        "--server-host",
        "-H",
        dest="host",
        default="cwop.aprs.net",
        type=str,
        help=f"Server IP or domain to listen (using default is not sufisent"
        "you may listen all servers using by this roundrobin DNS).",
    )

def prepare_callback(station, base_url, print_only=False):

    def publish_metric(packet):
        if packet.get("from") == station:
            print("Sending following packet: ")
            print(packet)
            url: str = urljoin(base_url, "weather-station/aprs-packet")
            if print_only:
                print(f"POSTING {packet} on {url}")
            else:
                r = requests.post(
                    url,
                    json={"raw": packet["raw"]},
                    auth=HTTPBasicAuth(LOGIN, PASSWORD),
                )
                if r.status_code != 200:
                    print(f"Something goes wrong, Ignoring... {r.reason}")
                    # raise RuntimeError(
                    #     f"Got following error while posting data: data to {url}: "
                    #     f"{r}"
                    # )

    return publish_metric

def listent_and_publish():
    parser = argparse.ArgumentParser(
        description="Read APRS-IS sensors metric and send state to home-thermostat"
    )
    common_settings(parser)
    args = parser.parse_args()

    print(f"listening station {args.station} {args.host} with {args.callsign}.")
    AIS = aprslib.IS(args.callsign, host=args.host)
    AIS.connect()
    print(f"running on {AIS.server}!")
    AIS.consumer(prepare_callback(args.station, args.base_url, print_only=args.print_only), raw=False)
