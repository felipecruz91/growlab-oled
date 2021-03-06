#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2014-2020 Richard Hull and contributors
# See LICENSE.rst for details.
# PYTHON_ARGCOMPLETE_OK

"""
Display basic system information.

Needs psutil (+ dependencies) installed::

  $ sudo apt-get install python-dev
  $ sudo -H pip install psutil
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

if os.name != 'posix':
    sys.exit('{} platform not supported'.format(os.name))

from demo_opts import get_device
from luma.core.render import canvas
from PIL import ImageFont

try:
    import psutil
except ImportError:
    print("The psutil library was not found. Run 'sudo -H pip install psutil' to install it.")
    sys.exit()

from sensors import growbme280, growbmp280, grownosensor

def bytes2human(n):
    """
    >>> bytes2human(10000)
    '9K'
    >>> bytes2human(100001221)
    '95M'
    """
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = int(float(n) / prefix[s])
            return '%s%s' % (value, s)
    return "%sB" % n

def disk_usage(dir):
    usage = psutil.disk_usage(dir)
    return "SD:  %s %.0f%%" \
        % (bytes2human(usage.used), usage.percent)

def stats(device, readings):
    # use custom font
    font_path = str(Path(__file__).resolve().parent.joinpath('fonts', 'C&C Red Alert [INET].ttf'))
    font2 = ImageFont.truetype(font_path, 12)

    with canvas(device) as draw:
        draw.text((0, 0), "Time: %s" % (readings["time"]), font=font2, fill="white")
        draw.text((0, 14), "Temp: %s C" % ('{:3.3}'.format(readings["temperature"])), font=font2, fill="white")
        draw.text((0, 26), "Humidity: %s%%" % ('{:3.3}'.format(readings["humidity"])), font=font2, fill="white")
        draw.text((0, 38), "Pressure: %s hPa" % ('{:5.5}'.format(readings["pressure"])), font=font2, fill="white")
        draw.text((0, 50), disk_usage('/'), font=font2, fill="white")

def main():
    sensor = None
    sensor_type = os.getenv("SENSOR_TYPE", "bme280")
    if sensor_type == "bme280":
        sensor = growbme280()
    if sensor_type == "bmp280":
        sensor = growbmp280()
    elif sensor_type == "none":
        sensor = grownosensor()

    while True:
        readings = sensor.get_readings()
        stats(device, readings)
        time.sleep(5)


if __name__ == "__main__":
    try:
        device = get_device()
        main()
    except KeyboardInterrupt:
        pass
