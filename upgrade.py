import csv
from netmiko import ConnectHandler


# visual separator
sep = '=' * 70


user = {
    'name': 'username',
    'password': 'password'
}


def fetch_devices(fin):
    """

    Fetches device data from CSV

    Arguments:
        fin {String} -- relative filename

    Returns:
        List -- List of dictionaries representing hostname & IP address of each device
    """
    device_list = []
    try:
        with open(fin) as devices:
            for row in csv.DictReader(devices):
                device_list.append(row)
    except Exception as e:
        print('There was a problem accessing the devices file...')
        print(e)
    return device_list


def connect_to(ip, username, password, attempt=0):
    """

    Connects to device

    Arguments:
        hostname {String} -- Device Hostname
        ip {String} -- Device IP Address

    Returns:
        Object | Boolean -- Connection Handler or False
    """
    print('\n' + sep)
    print('==> Connecting to {0}'.format(ip))
    # Device connection details
    device_dict = {
        'device_type': 'cisco_ios',
        'ip':  ip,
        'username': username,
        'password': password,
    }
    try:
        connection = ConnectHandler(**device_dict)
        print('==> Connected')
        return connection
    except Exception as e:
        print('==> Error connecting to {0}'.format(ip))
        print('==> ' + str(e))
        print('==> Re-trying...{0}'.format(attempt))
        connect_to(ip, username, password, attempt + 1)



def apply_command(net_connect, command):
    res = net_connect.send_command(command)
    if 'Unable to create temp dir' in res:
        print('==> Device already in the process of upgrading')
    else:
        print('==> Starting upgrade...')
    print('==> Exiting...')


def check_status(ip):
    verify_command = 'sh ver'
    version = 'Version 15.2(2)E5'
    username = user['name']
    password = user['password']
    net_connect = connect_to(ip, username, password)
    if net_connect:
        res = net_connect.send_command_expect(verify_command)
        print('==> {0}'.format(res.split('\n')[0]))
        if version in res:
            return True
        else:
            return False


def main():
    upgrade_command = 'archive download-sw /overwrite /force-reload tftp://10.1.240.245/c2960-lanbasek9-tar.152-2.E5.tar'
    username = user['name']
    password = user['password']
    devices = fetch_devices('devices.csv')
    ip_list = [d['ip'] for d in devices]
    for ip in ip_list:
        if check_status(ip):
            print('{0}\n==> {1} already upgraded\n{2}'.format(sep, ip, sep))
        else:
            net_connect = connect_to(ip, username, password)
            apply_command(net_connect, upgrade_command)


if __name__ == "__main__":
    main()
