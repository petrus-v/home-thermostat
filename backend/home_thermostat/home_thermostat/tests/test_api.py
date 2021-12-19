from datetime import datetime
from decimal import Decimal as D

import pytest
import respx
from anyblok_fastapi.conftest import webserver  # noqa: F401
from conftest import get_device
from sqlalchemy.orm.exc import NoResultFound

from home_thermostat.home_thermostat.schemas.devices import (
    RelayState,
    WeatherStationState,
    APRSWeatherStationPacket,
)

# from testfixtures import Replace, test_datetime


@pytest.fixture
def some_states(
    rollback_registry,
    engine,
    water_departures,
    water_returns,
    fioul_gauge,
    weather_station,
):
    generate_states(rollback_registry.Iot.State.Relay, engine)
    rollback_registry.Iot.State.Thermometer.insert(
        device=water_departures,
        create_date=datetime(2020, 6, 15, 11, 37),
        celsius=D("40.321"),
    )
    rollback_registry.Iot.State.Thermometer.insert(
        device=water_departures,
        create_date=datetime(2020, 6, 15, 11, 42),
        celsius=D("45.321"),
    )
    rollback_registry.Iot.State.Thermometer.insert(
        device=water_returns,
        create_date=datetime(2020, 6, 15, 11, 40),
        celsius=D("30.456"),
    )
    rollback_registry.Iot.State.FuelGauge.insert(
        device=fioul_gauge,
        create_date=datetime(2020, 6, 1, 8, 40),
        level=1105,  # 1.105 meter
    )
    rollback_registry.Iot.State.WeatherStation.insert(
        device=weather_station,
        create_date=datetime(2020, 6, 1, 8, 40),
        sensor_date=datetime(2020, 6, 1, 8, 39),
        wind_direction=52,
        wind_speed=2.2352,
        wind_gust=5.81152,
        temperature=3.333333333333333,
        rain_1h=0.0,
        rain_24h=1.016,
        rain_since_midnight=0.254,
        humidity=95,
        pressure=1027.1,
        luminosity=0,
    )
    rollback_registry.flush()


@pytest.fixture
def some_desired_states(rollback_registry, engine):
    generate_states(rollback_registry.Iot.State.DesiredRelay, engine)
    rollback_registry.flush()


def generate_states(State, engine):
    State.insert(
        device=engine,
        create_date=datetime(2020, 6, 15, 9, 42),
        is_open=True,
    )
    State.insert(
        device=engine,
        create_date=datetime(2020, 6, 15, 9, 55),
        is_open=False,
    )
    State.insert(
        device=engine,
        create_date=datetime(2020, 6, 15, 10, 42),
        is_open=True,
    )
    State.insert(
        device=engine,
        create_date=datetime(2020, 6, 15, 11, 42),
        is_open=False,
    )


@pytest.mark.parametrize(
    "device_type,device_id,expected_data,desired",
    (
        (
            "relay",
            "engine",
            {
                "is_open": False,
                "create_date": "2020-06-15T11:42:00+00:00",
                "device": {"code": "ENGINE", "name": "Circulateur"},
            },
            "",
        ),
        (
            "relay",
            "engine",
            {
                "is_open": False,
                "create_date": "2020-06-15T11:42:00+00:00",
                "device": {"code": "ENGINE", "name": "Circulateur"},
            },
            "/desired",
        ),
        (
            "thermometer",
            "temperature_sensor_28-01193a4a4aa2",
            {
                "celsius": 45.321,
                "create_date": "2020-06-15T11:42:00+00:00",
                "device": {"code": "28-01193a4a4aa2", "name": "Départ"},
            },
            "",
        ),
        (
            "fuel-gauge",
            "fuel-gauge",
            {
                "level": 1105,
                "create_date": "2020-06-01T08:40:00+00:00",
                "device": {"code": "FUEL", "name": "Fioul"},
            },
            "",
        ),
        (
            "weather-station",
            "FW5282_weather_station",
            {
                "wind_direction": 52,
                "wind_speed": 2.2352,
                "wind_gust": 5.81152,
                "temperature": 3.333333333333333,
                "rain_1h": 0.0,
                "rain_24h": 1.016,
                "rain_since_midnight": 0.254,
                "humidity": 95,
                "pressure": 1027.1,
                "luminosity": 0,
                "create_date": "2020-06-01T08:40:00+00:00",
                "sensor_date": "2020-06-01T08:39:00+00:00",
                "device": {"code": "FW5282", "name": "CWOP Weather Station: FW5282"},
            },
            "",
        ),
    ),
)
def test_api_device_code_state_get_latest_state(
    rollback_registry,
    webserver,
    some_states,
    some_desired_states,
    device_type,
    device_id,
    expected_data,
    desired,
):
    device = get_device(rollback_registry, device_id)
    response = webserver.get(f"/api/device/{device_type}/{device.code}{desired}/state")
    assert response.status_code == 200
    assert response.json() == expected_data


@pytest.mark.parametrize(
    "desired",
    ("", "/desired"),
)
def test_api_device_code_state_get_latest_state_not_defined(
    rollback_registry, webserver, engine, desired
):
    response = webserver.get(f"/api/device/relay/{engine.code}{desired}/state")
    assert response.status_code == 200
    results = response.json()
    del results["create_date"]
    assert results == {
        "is_open": True,
        "device": {"code": engine.code, "name": engine.name},
    }


@pytest.mark.parametrize(
    "device,desired",
    (
        ("thermometer", ""),
        ("fuel-gauge", ""),
        ("relay", ""),
        ("relay", "/desired"),
        ("weather-station", ""),
    ),
)
def test_api_device_code_state_wrong_code(
    rollback_registry, webserver, some_states, device, desired
):
    with pytest.raises(NoResultFound):
        response = webserver.get(f"/api/device/{device}/UNKNOWN{desired}/state")


def test_save_device_state(rollback_registry, webserver, engine):
    registry = rollback_registry
    State = registry.Iot.State
    count_before = State.query().count()
    response = webserver.post(
        f"/api/device/relay/{engine.code}/state", json={"is_open": True}
    )
    assert response.status_code == 200, str(response)
    assert count_before + 1 == State.query().count()


def test_save_device_state_unkwon_device(rollback_registry, webserver):
    registry = rollback_registry
    State = registry.Iot.State
    count_before = State.query().count()
    with pytest.raises(NoResultFound):
        webserver.post(f"/api/device/relay/UNKNOWN/state", data='{"is_open": true}')


def test_save_device_state_wrong_format(rollback_registry, webserver, engine):
    registry = rollback_registry
    State = registry.Iot.State
    count_before = State.query().count()
    response = webserver.post(
        f"/api/device/relay/{engine.code}/state",
        data='{"is_open": "wrong type", "extra": true}',
    )
    assert response.status_code == 422, str(response)
    assert count_before + 0 == State.query().count()


def test_save_device_relay_desired_state(rollback_registry, webserver, engine):
    registry = rollback_registry
    State = registry.Iot.State.DesiredRelay
    count_before = State.query().count()
    response = webserver.post(
        f"/api/device/relay/{engine.code}/desired/state",
        json={"is_open": True},
    )
    assert response.status_code == 200, str(response)
    assert count_before + 1 == State.query().count()


@pytest.mark.parametrize(
    "device,data",
    (
        ("relay", {"is_open": True}),
        # ("thermometer", {"celsius": D("20.3")}),
        # ("fuel-gauge", {"level": 1234}),
    ),
)
def test_save_device_desired_state_unkwon_device(
    rollback_registry, webserver, some_desired_states, device, data
):
    registry = rollback_registry
    with pytest.raises(NoResultFound):
        webserver.post(f"/api/device/{device}/UNKNOWN/desired/state", json=data)


@pytest.mark.parametrize(
    "device,data",
    (
        ("relay", {"is_open": "wrong type", "extra": "wrong extra field"}),
        # ("thermometer", {"celsius": False, "extra": "wrong extra field"}),
        # ("fuel-gauge", {"level": "wrong type", "extra": "wrong extra field"}),
    ),
)
def test_save_device_desired_state_wrong_format(
    rollback_registry, webserver, engine, device, data
):
    registry = rollback_registry
    State = registry.Iot.State
    count_before = State.query().count()
    response = webserver.post(
        f"/api/device/{device}/{engine.code}/desired/state", json=data
    )
    assert response.status_code == 422, str(response)
    assert count_before + 0 == State.query().count()


@pytest.mark.parametrize(
    "payload,response",
    (
        ({"mode": "manual"}, {"mode": "manual"}),
        ({"mode": "thermostat"}, {"mode": "thermostat"}),
    ),
)
def test_save_thermostat_mode(rollback_registry, webserver, payload, response):
    r = webserver.post(f"/api/mode", json=payload)
    assert r.status_code == 200, str(r)
    assert r.json() == response


@pytest.mark.parametrize(
    "mode,response",
    (
        ("manual", {"mode": "manual"}),
        ("thermostat", {"mode": "thermostat"}),
    ),
)
def test_get_thermostat_mode(rollback_registry, webserver, mode, response):
    registry = rollback_registry
    registry.System.Parameter.set("mode", mode)
    registry.flush()
    r = webserver.get(
        f"/api/mode",
    )
    assert r.status_code == 200, str(r)
    assert r.json() == response


def test_set_get_mode(
    rollback_registry,
    webserver,
):
    registry = rollback_registry
    mode = {"mode": "thermostat"}
    r = webserver.post(f"/api/mode", json=mode)
    assert r.status_code == 200, str(r)
    assert r.json() == mode
    r = webserver.get(
        f"/api/mode",
    )
    assert r.status_code == 200, str(r)
    assert r.json() == mode


def test_set_test_range(rollback_registry, webserver):
    registry = rollback_registry
    data = {"start": "08:11", "end": "3:22:30", "celsius": 15.5}
    expected_data = {"start": "08:11:00", "end": "03:22:30", "celsius": 15.5}
    r = webserver.post(f"/api/thermostat/range/22", json=data)
    assert r.status_code == 200, str(r)
    assert r.json() == expected_data

    data2 = {"start": "08:23", "end": "23:1", "celsius": 20.5}
    expected_data2 = {"start": "08:23:00", "end": "23:01:00", "celsius": 20.5}
    r = webserver.post(f"/api/thermostat/range/22", json=data2)
    assert r.status_code == 200, str(r)
    assert r.json() == expected_data2

    r = webserver.get(
        f"/api/thermostat/range/22",
    )
    assert r.status_code == 200, str(r)
    assert r.json() == expected_data2


def test_parse_aprs_packet():
    # {
    #     'raw': 'FW5282>APRS,TCPXX*,qAX,CWOP-5:@192116z4759.58N/00227.12E_052/005g013t038r000p004P001h95b10271L000.DsVP',
    #     'from': 'FW5282',
    #     'to': 'APRS',
    #     'path': ['TCPXX*', 'qAX', 'CWOP-5'],
    #     'via': 'CWOP-5',
    #     'messagecapable': True,
    #     'raw_timestamp': '192116z',
    #     'timestamp': 1639948560,
    #     'format': 'uncompressed',
    #     'posambiguity': 0,
    #     'symbol': '_',
    #     'symbol_table': '/',
    #     'latitude': 47.993,
    #     'longitude': 2.452,
    #     'comment': '.DsVP',
    #     'weather': {
    #         'wind_direction': 52,
    #         'wind_speed': 2.2352,
    #         'wind_gust': 5.81152,
    #         'temperature': 3.333333333333333,
    #         'rain_1h': 0.0,
    #         'rain_24h': 1.016,
    #         'rain_since_midnight': 0.254,
    #         'humidity': 95,
    #         'pressure': 1027.1,
    #         'luminosity': 0
    #     }
    # }

    raw_data = APRSWeatherStationPacket(raw="FW5282>APRS,TCPXX*,qAX,CWOP-5:@192116z4759.58N/00227.12E_052/005g013t038r000p004P001h95b10271L000.DsVP")
    weather_station_state : WeatherStationState = raw_data.parse()

    # assert weather_station_state.station_id == "FW5282"
    assert weather_station_state.sensor_date == datetime.fromtimestamp(1639948560)
    assert weather_station_state.wind_direction == D('52')
    assert weather_station_state.wind_speed == D('2.2352')
    assert weather_station_state.wind_gust == D('5.81152')
    assert weather_station_state.temperature == D('3.333333333333333')
    assert weather_station_state.rain_1h == D('0.0')
    assert weather_station_state.rain_24h == D('1.016')
    assert weather_station_state.rain_since_midnight == D('0.254')
    assert weather_station_state.humidity == D('95')
    assert weather_station_state.pressure == D('1027.1')
    assert weather_station_state.luminosity == D('0')


def test_save_weather_station_state(rollback_registry, webserver, weather_station):
    registry = rollback_registry
    State = registry.Iot.State
    count_before = State.query().count()
    response = webserver.post(
        f"/api/device/weather-station/{weather_station.code}/state",
        json={
            'sensor_date': "2020-06-15T11:42:00+00:00",
            'wind_direction': 52,
            'wind_speed': 2.2352,
            'wind_gust': 5.81152,
            'temperature': 3.333333333333333,
            'rain_1h': 0.0,
            'rain_24h': 1.016,
            'rain_since_midnight': 0.254,
            'humidity': 95,
            'pressure': 1027.1,
            'luminosity': 0
        }
    )
    assert response.status_code == 200, str(response)
    assert count_before + 1 == State.query().count()


def test_save_weather_station_packet(rollback_registry, webserver, weather_station):
    registry = rollback_registry
    State = registry.Iot.State
    count_before = State.query().count()
    response = webserver.post(
        f"/api/device/weather-station/aprs-packet",
        json={
            'raw': "FW5282>APRS,TCPXX*,qAX,CWOP-5:@192116z4759.58N/00227.12E_052/005g013t038r000p004P001h95b10271L000.DsVP",
        }
    )
    assert response.status_code == 200, str(response)
    assert count_before + 1 == State.query().count()
