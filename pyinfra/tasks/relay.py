import os
from pyinfra import host
from pyinfra.operations import files, pip, systemd


files.directory(
    name='Ensure relay direcory exists',
    path=host.data.relay_card_app_dir,
    present=True,
    user=None,
    group=None,
    mode=None,
    recursive=False,
)

project = files.sync(
    name='Ensure relay direcory is synced',
    src="files/relay",
    dest=host.data.relay_card_app_dir,
    user=host.data.relay_card_app_user,
    group=None,
    delete=True,
    exclude=None,
    add_deploy_dir=True,
    exclude_dir=["__pycache__", "*.egg-info"],
)

# https://docs.pyinfra.com/en/1.x/operations/pip.html
install_relay = pip.packages(
    name='Install latest requirements.txt',
    packages=["pip", "wheel", host.data.relay_card_app_dir],
    present=True,
    latest=project.changed,
    requirements=os.path.join(host.data.relay_card_app_dir, "requirements.txt"),
    pip='pip',
    virtualenv=host.data.relay_card_venv_path,
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
#     name='Create relay conf file (with password)',
#     src='templates/relay.conf.j2',
#     dest='/etc/relay.conf',
#     user=host.data.relay_card_app_user,
#     group=host.data.relay_card_app_user,
#     mode="600",
# )


for unit_name, device, pin, on_calendar in [
    (
        "relay-burner",
        "BURNER",
        host.data.relay_card_burner_pin,
        host.data.relay_card_burner_on_calendar,
    ),
    (
        "relay-engine",
        "ENGINE",
        host.data.relay_card_engine_pin,
        host.data.relay_card_engine_on_calendar,
    ),
]:
    service_unit = files.template(
        name=f"Configure systemd { unit_name }.service",
        src="templates/relay.service.j2",
        dest=f"/etc/systemd/system/{ unit_name }.service",
        user="root",
        group="root",
        mode="755",
        create_remote_dir=True,
        sudo=True,
        device=device,
        pin=pin,
    )
    timer_unit = files.template(
        name=f"Configure systemd {unit_name}.timer",
        src="templates/relay.timer.j2",
        dest=f"/etc/systemd/system/{ unit_name }.timer",
        user="root",
        group="root",
        mode="755",
        create_remote_dir=True,
        sudo=True,
        relay_service_unit_name=unit_name,
        device=device,
        pin=pin,
        on_calendar=on_calendar
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
