# APRS STATION

Small script to subscribe to APRS-IS message
and send measure to home thermostat server.

# RESOURCES

POC with comment

```python
import requests
import aprslib
import os
from urllib.parse import urljoin

from requests.auth import HTTPBasicAuth

DEFAULT_BASE_URL = os.environ["THERMOSTAT_BACKEND_URL"] + "/api/device/"
LOGIN = os.environ["THERMOSTAT_BACKEND_LOGIN"]
PASSWORD = os.environ["THERMOSTAT_BACKEND_PASSWORD"]
DEVICE = os.environ.get("THERMOSTAT_APRS_STATION_DEVICE", "28-01193a503a1a")

def callback(packet):
    if packet.get("from") == "FW5282":
        # In [17]: datetime.fromtimestamp(aprslib.parse("FW5282>APRS,TCPXX*,qAX,CWOP-2:@190136z4759.58N/00227.12E_0
        #     ...: 41/008g012t037r000p008P000h96b10324L000.DsVP").get("timestamp"))
        # Out[17]: datetime.datetime(2021, 12, 19, 2, 36)
        print("Sending following packet: ")
        print(packet)
        url: str = urljoin(DEFAULT_BASE_URL, f"thermometer/{DEVICE}/state")
        r = requests.post(
            url,
            json={"celsius": packet["weather"]["temperature"]},
            auth=HTTPBasicAuth(LOGIN, PASSWORD),
        )
        if r.status_code != 200:
            raise RuntimeError(
                f"Got following error while posting data: data to {url}: "
                f"{r}"
            )
# http://www.wxqa.com/
# http://www.aprs2.net/
# trouver le serveur: http://www.wxqa.com/faq.html / http://www.wxqa.com/servers2use.html
# visualiser les données de la balise: http://www.findu.com/cgi-bin/wxpage.cgi?call=FW5282
# activité de la balise: https://www.aprsdirect.com/details/activity/sid/2196260

# export CWOP_IP=63.251.153.99 && python external-temp.py
# export CWOP_IP=137.26.70.99 && python external-temp.py
# export CWOP_IP=129.15.108.117 && python external-temp.py
# export CWOP_IP=44.155.254.4 && python external-temp.py
# export CWOP_IP=129.15.108.116 && python external-temp.py
# export CWOP_IP=85.188.1.27 && python external-temp.py
# export CWOP_IP=66.151.32.203 && python external-temp.py
host = os.environ.get("CWOP_IP", "cwop.aprs.net")
print(f"running on {host}!")
AIS = aprslib.IS("FW5282", host=host)
# AIS = aprslib.IS("FW5282", host="cwop.aprs.net", port=10152)
# AIS = aprslib.IS("FW5282", host="cwop.aprs.net")
# http://www.aprs-is.net/javAPRSFilter.aspx
# AIS.set_filter()
AIS.connect()
print(f"running on {AIS.server}!")
AIS.consumer(callback, raw=False)


# get data: 
# https://weather.gladstonefamily.net/site/search?site=F5282;Get%20information=Get%20information;metric=1;days=3#Data
# https://weather.gladstonefamily.net/cgi-bin/wxobservations.pl?site=F5282&days=1
# http://www.findu.com/cgi-bin/wx.cgi?call=FW5282&units=metric

# Peut-être en parsant simplement les dernières données ici:
# http://www.findu.com/cgi-bin/raw.cgi?call=FW5282&start=1&length=1&time=0
# suffirait http://www.findu.com/cgi-bin/raw.cgi?call=FW5282&start=1&time=0

# pip install dnspython
# from dns import resolver
# [d.address for d in resolver.resolve('cwop.aprs.net')]
```