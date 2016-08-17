import csv
import os
from netmiko import ConnectHandler


user = {
    'name': 'username',
    'password': 'password'
}


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
    print('==> Applying {0}'.format(name))
    try:
        with open(cf) as f:
            commands = [line.strip() for line in f.readlines()]
            return commands
    except Exception as e:
        print('There was a problem accessing the {0} file...'.format(name))
        print(e)
        return False


def connect_to(hostname, ip, username, password):
    print('\n' + sep)
    print('    connecting to {0} on {1}'.format(hostname, ip))
    print(sep + '\n')
    device_dict = {
        'device_type': 'cisco_ios',
        'ip':  ip,
        'username': username,
        'password': password
    }
    try:
        connection = ConnectHandler(**device_dict)
        print('==> Connected')
        return connection
    except Exception as e:
        print('==> Error connecting to {0}'.format(hostname))
        print('==> ' + str(e))
        return False


def apply_commands(net_connect, hostname, commands):
    print('\n' + sep)
    print('==> Sending commands...')
    print(sep)
    command = net_connect.send_config_set(commands)
    print(command)
    print('\n' + sep + '\n')
    print('==> Writing new commands to memory...')
    enter = net_connect.send_command('wr')
    print(enter)


def write_show_run(hostname, data):
    print('==> Writing final configuration to file...')
    try:
        filename = hostname + '.txt'
        fout = open(filename, 'w')
        fout.write(data)
        print('==> Configuration written to:\n\n    {0}'.format(os.path.join(os.getcwd(), filename)))
    except Exception as e:
        print('==> Error writing configuration to file...')
        print('==> ' + str(e))


def main(devices, commands_dir, username=user['name'], password=user['password']):
    commands_files = os.listdir(commands_dir)
    for device in devices:
        hostname = device['hostname']
        ip = device['ip']
        net_connect = connect_to(hostname, ip, username, password)
        if net_connect:
            for cf in commands_files:
                commands = fetch_commands(cf)
                if commands:
                    apply_commands(net_connect, hostname, commands)


if __name__ == "__main__":
    devices_file = 'devices.csv'
    commands_dir = 'commands'
    devices = fetch_devices(devices_file)
    if devices:
        main(devices, commands_dir)
    else:
        print('==> No devices available.')
