#!/usr/bin/env python3
"""

To run the script, do the following:
$ pip3 install pytradfri
$ Download this file (example_sync.py)
$ python3 example_sync.py <IP>

Where <IP> is the address to your IKEA gateway. The first time
running you will be asked to input the 'Security Code' found on
the back of your IKEA gateway.
"""

# Hack to allow relative import above top level package
import sys
import os
folder = os.path.dirname(os.path.abspath(__file__))  # noqa
sys.path.insert(0, os.path.normpath("%s/.." % folder))  # noqa

from pytradfri import Gateway
from pytradfri.api.libcoap_api import APIFactory
from pytradfri.error import PytradfriError
from pytradfri.util import load_json, save_json

import uuid
import argparse
import threading
import time

CONFIG_FILE = 'tradfri_standalone_psk.conf'

RED_XY = (42926, 21299)

parser = argparse.ArgumentParser()
parser.add_argument('host', metavar='IP', type=str,
                    help='IP Address of your Tradfri gateway')
parser.add_argument('-K', '--key', dest='key', required=False,
                    help='Security code found on your Tradfri gateway')
args = parser.parse_args()


if args.host not in load_json(CONFIG_FILE) and args.key is None:
    print("Please provide the 'Security Code' on the back of your "
          "Tradfri gateway:", end=" ")
    key = input().strip()
    if len(key) != 16:
        raise PytradfriError("Invalid 'Security Code' provided.")
    else:
        args.key = key


def observe(api, device):
    def callback(updated_device):
        light = updated_device.light_control.lights[0]
        print("Received message for: %s" % light)

    def err_callback(err):
        print(err)

    def worker():
        api(device.observe(callback, err_callback, duration=120))

    threading.Thread(target=worker, daemon=True).start()
    print('Sleeping to start observation task')
    time.sleep(1)


def run():
    # Assign configuration variables.
    # The configuration check takes care they are present.
    conf = load_json(CONFIG_FILE)

    try:
        identity = conf[args.host].get('identity')
        psk = conf[args.host].get('key')
        api_factory = APIFactory(host=args.host, psk_id=identity, psk=psk)
    except KeyError:
        identity = uuid.uuid4().hex
        api_factory = APIFactory(host=args.host, psk_id=identity)

        try:
            psk = api_factory.generate_psk(args.key)
            print('Generated PSK: ', psk)

            conf[args.host] = {'identity': identity,
                               'key': psk}
            save_json(CONFIG_FILE, conf)
        except AttributeError:
            raise PytradfriError("Please provide the 'Security Code' on the "
                                 "back of your Tradfri gateway using the "
                                 "-K flag.")

    api = api_factory.request

    gateway = Gateway()

    devices_command = gateway.get_devices()
    devices_commands = api(devices_command)
    devices = api(devices_commands)

    lights = [dev for dev in devices if dev.has_light_control]

    # Lights can be accessed by its index, so lights[1] is the second light
    # Print all lights
    if lights:
        for i, light in enumerate(lights):
            api(light.light_control.set_xy_color(RED_XY[0], RED_XY[1]))
            time.sleep(1)
            api(light.light_control.set_dimmer(254))
            #for j in range(1, 254, 10):
            #    api(light.light_control.set_dimmer(j))
            #    time.sleep(0.1)

    else:
        print("No lights found!")
        light = None

run()
