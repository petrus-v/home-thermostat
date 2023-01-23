from setuptools import setup, find_packages
from urllib.parse import parse_qs, urlparse


def parse_requirements(file):
    required = []
    with open(file) as f:
        for req in f:
            req = req.strip()
            if req.startswith("#"):
                continue
            if "egg" in req:
                if req.startswith("-e"):
                    vcs_pkg = urlparse(req.split(" ")[1])
                else:
                    vcs_pkg = urlparse(req)
                req = parse_qs(vcs_pkg.fragment)["egg"][0]
            required.append(req)
    return required


requirements = parse_requirements("requirements.txt")

setup(
    name='relay',
    version='0.1',
    author='Pierre Verkest',
    author_email='pierreverkest84@gmail.com',
    description='Raspberry Pi home thermostat Relay card',
    long_description='Script do turn on/off burner and engine boiler '
                     'using AZ relay card: 2PH63091A',
    download_url='http://github.com/petrus-v/home-thermostat',
    install_requires=requirements,
    license='unlicense.org',
    keywords=[
        'raspberrypi',
        'gpio',
        'relay',
    ],
    entry_points={
        'console_scripts': [
            'relay-publish-state=relay.cli:read',
            'relay-set=relay.cli:write',
        ],
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ]
)