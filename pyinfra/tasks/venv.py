from pyinfra import host
from pyinfra.operations import apt

apt.packages(
    name='Ensure the python3-venv apt package is installed',
    packages=['python3-venv'],
    sudo=True,  # use sudo when installing the packages
)
