import os

from pyinfra import host, local
from pyinfra.operations import files, pip, systemd, server


# local.include("facts/DS18B20Sensor.py")
# temperature_sensors1 = host.fact.ds18_b20_sensor()
files.directory(
    name='Ensure weather_station direcory exists',
    path=host.data.weather_station_app_dir,
    present=True,
    assume_present=True,
    user=None,
    group=None,
    mode=None,
    recursive=False,
)

project = files.sync(
    name='Ensure weather_station direcory is synced',
    src="files/aprs-station",
    dest=host.data.weather_station_app_dir,
    user=host.data.weather_station_app_user,
    group=None,
    delete=True,
    exclude=None,
    exclude_dir=["__pycache__", "*.egg-info"],
    add_deploy_dir=True,
)

# https://docs.pyinfra.com/en/1.x/operations/pip.html
install_temperature = pip.packages(
    name='Install latest requirements.txt weather_station',
    packages=["pip", "wheel", host.data.weather_station_app_dir],
    present=True,
    latest=project.changed,
    requirements=os.path.join(host.data.weather_station_app_dir, "requirements.txt"),
    pip='pip',
    virtualenv=host.data.weather_station_venv_path,
    virtualenv_kwargs={
        "python": "python3",
        "venv": True,
        "site_packages": False,
        "always_copy": False,
        "present": True,
    }, 
    extra_install_args=None,
)

# TODO: first implement
# files.template(
#     name='Create temperature conf file (with password)',
#     src='templates/temperature.conf.j2',
#     dest='/etc/temperature.conf',
#     user=host.data.temperature_card_app_user,
#     group=host.data.temperature_card_app_user,
#     mode="600",
# )


unit_name = "station-aprs@"

service_unit = files.template(
    name=f"Configure systemd { unit_name }.service",
    src="templates/station-aprs.service.j2",
    dest=f"/etc/systemd/system/{ unit_name }.service",
    user="root",
    group="root",
    mode="755",
    create_remote_dir=True,
    sudo=True,
)

for domain in host.data.aprs_domains:
    systemd.service(
        name=f"Ensure {unit_name}{domain}.service is enabled and running",
        service=f"{unit_name}{domain}.service",
        running=True,
        # reloaded not applicable for *.timer unit use restart instead
        # reloaded=timer_unit.changed or service_unit.changed,
        restarted=service_unit.changed,
        command=None,
        enabled=True,
        daemon_reload=service_unit.changed,
        sudo=True,
    )
