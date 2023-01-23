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
    name='temperature',
    version='0.1',
    author='Pierre Verkest',
    author_email='pierreverkest84@gmail.com',
    description='Raspberry Pi home thermostat Relay card',
    long_description='Script to publish temperatures',
    download_url='http://github.com/petrus-v/home-thermostat',
    install_requires=requirements,
    license='unlicense.org',
    keywords=[
        'raspberrypi',
        'gpio',
        'sensor',
        'temperature',
    ],
    entry_points={
        'console_scripts': [
            'temperature-publish-state=temperature.cli:read',
        ],
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ]
)