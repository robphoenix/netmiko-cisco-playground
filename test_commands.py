import csv
import os
from pprint import pprint


# visual separator
sep = '=' * 70


def fetch_devices(fin):
    device_list = []
    try:
        with open(fin) as devices:
            for row in csv.DictReader(devices):
                device_list.append(row)
    except Exception as e:
        print('There was a problem accessing the devices file...')
        print(e)
    return device_list


def fetch_commands(cf):
    (name, ext) = os.path.splitext(cf)
    print('==> Applying {0} commands'.format(name))
    try:
        with open(cf) as f:
            commands = [line.strip() for line in f.readlines()]
            return commands
    except Exception as e:
        print('There was a problem accessing the {0} file...'.format(name))
        print(e)
        return False


def main(devices, commands_dir):
    commands_files = os.listdir(commands_dir)
    for device in devices:
        for cf in commands_files:
            cfp = os.path.join(commands_dir, cf)
            commands = fetch_commands(cfp)
            if commands:
                pprint(commands)


if __name__ == "__main__":
    devices_file = 'devices.csv'
    commands_dir = 'commands'
    devices = fetch_devices(devices_file)
    if devices:
        main(devices, commands_dir)
    else:
        print('==> No devices available.')
