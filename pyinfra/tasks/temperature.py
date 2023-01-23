import os

from pyinfra import host, local
from pyinfra.operations import files, pip, systemd, server


# local.include("facts/DS18B20Sensor.py")
# temperature_sensors1 = host.fact.ds18_b20_sensor()

files.directory(
    name='Ensure temperature direcory exists',
    path=host.data.temperature_card_app_dir,
    present=True,
    assume_present=True,
    user=None,
    group=None,
    mode=None,
    recursive=False,
)

project = files.sync(
    name='Ensure temperature direcory is synced',
    src="files/temperature",
    dest=host.data.temperature_card_app_dir,
    user=host.data.temperature_card_app_user,
    group=None,
    delete=True,
    exclude=None,
    exclude_dir=["__pycache__", "*.egg-info"],
    add_deploy_dir=True,
)

# https://docs.pyinfra.com/en/1.x/operations/pip.html
install_temperature = pip.packages(
    name='Install latest requirements.txt',
    packages=["pip", "wheel", host.data.temperature_card_app_dir],
    present=True,
    latest=project.changed,
    requirements=os.path.join(host.data.temperature_card_app_dir, "requirements.txt"),
    pip='pip',
    virtualenv=host.data.temperature_card_venv_path,
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

boot_config = files.line(
    name="Enable the 1-wire bus, setting /boot/config.txt file",
    path="/boot/config.txt",
    line="dtoverlay=w1-gpio",
    present=True,
    replace=None,
    flags=None,
    backup=False,
    interpolate_variables=False,
    assume_present=False,
    sudo=True,
)

if boot_config.changed:
    server.reboot(delay=10, interval=1, reboot_timeout=120, sudo=True)

files.put(
    name="Allow pggpiod to read wire-1 temperature sensor devices 28-*",
    src="files/pigpio/access",
    dest="/opt/pigpio/access",
    user="root",
    group="root",
    mode="655",
    add_deploy_dir=True,
    create_remote_dir=True,
    force=False,
    assume_exists=False,
    sudo=True
)

files.put(
    name="Copy pigpiod-restart.service",
    src="files/pigpio/pigpiod-restart.service",
    dest="/etc/systemd/system/pigpiod-restart.service",
    user="root",
    group="root",
    mode="755",
    create_remote_dir=True,
    sudo=True
)



unit_name = "thermometers"
device = "Deaparture and Arrival"

service_unit = files.template(
    name=f"Configure systemd { unit_name }.service",
    src="templates/thermometer.service.j2",
    dest=f"/etc/systemd/system/{ unit_name }.service",
    user="root",
    group="root",
    mode="755",
    create_remote_dir=True,
    sudo=True,
    device=device,
)
timer_unit = files.template(
    name=f"Configure systemd {unit_name}.timer",
    src="templates/thermometer.timer.j2",
    dest=f"/etc/systemd/system/{ unit_name }.timer",
    user="root",
    group="root",
    mode="755",
    create_remote_dir=True,
    sudo=True,
    thermometer_service_unit_name=unit_name,
    device=device,
    on_calendar=host.data.temperature_card_engine_on_calendar
)

systemd.service(
    name=f"Ensure {unit_name}.timer is enabled and running",
    service=f"{ unit_name }.timer",
    running=True,
    # reloaded not applicable for *.timer unit use restart instead
    # reloaded=timer_unit.changed or service_unit.changed,
    restarted=timer_unit.changed or service_unit.changed,
    command=None,
    enabled=True,
    daemon_reload=timer_unit.changed or service_unit.changed,
    sudo=True,
)
