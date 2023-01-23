import os
weather_station_app_user = "pi"
weather_station_app_user_home = "/home/pi"
weather_station_app_dir = os.path.join(weather_station_app_user_home, "weather_station")
weather_station_venv_path = os.path.join(weather_station_app_user_home, "weather-station-venv")

aprs_domains = [
    "cwop1.aprs.net",
    "cwop2.aprs.net",
    "cwop3.aprs.net",
    "cwop4.aprs.net",
    "cwop5.aprs.net",
    "cwop6.aprs.net",
    "cwop7.aprs.net",
]
