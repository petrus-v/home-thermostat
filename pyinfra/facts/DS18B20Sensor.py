from os import path
from pyinfra.api import FactBase


class DS18B20Sensor(FactBase):
    '''
    Returns a list of files from a start point, recursively using find.
    '''

    def command(self):
        # Find files in the given location
        return 'ls -d /sys/bus/w1/devices/28-*'

    def process(self, output):
        return [path.basename(directory_path) for directory_path in output]  # return the list of lines (files) as-is
