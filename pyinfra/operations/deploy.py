from pyinfra import host, local


# if "card" in host.groups:
#     local.include("tasks/common.py")
#     local.include("tasks/venv.py")

# if "relay_card" in host.groups:
#     local.include("tasks/relay.py")

# if "temperature_card" in host.groups:
#     local.include("tasks/temperature.py")

if "weather_station" in host.groups:
    local.include("tasks/weather_station.py")