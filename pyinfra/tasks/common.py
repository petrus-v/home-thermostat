from pyinfra.operations import apt, systemd

apt.packages(
    name='Ensure the pigpiod apt package is installed',
    packages=['pigpiod'],
    sudo=True,  # use sudo when installing the packages
)


systemd.service(
    name='Enable and start pigpiod service',
    service='pigpiod.service',
    running=True,
    # restarted=True,
    enabled=True,
    sudo=True,
)
