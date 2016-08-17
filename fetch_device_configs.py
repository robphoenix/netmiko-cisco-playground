import csv
import os
import datetime
import getpass
from netmiko import ConnectHandler


# visual separator
sep = '=' * 70
# Global dictionary to store results of operation
# results of actions for each device: Failure | Success
result_dict = {}


def get_user_info():
  """

  Get devices_file, username & password input from user

  No Arguments

  No Returns
  """
  print(sep)
  print('\nPlease enter details for devices.\n')
  devices_file = input('Devices csv filename (default: \'devices.csv\'): ')
  username = input('Username for devices: ')
  password = getpass.getpass(prompt="Password for devices (this will be hidden): ")
  devices_file = devices_file or 'devices.csv'
  print(sep)
  print('\nYou entered the following details:\n')
  print('Devices File: ', devices_file)
  if username:
    print('Username: ', username)
  else:
    print('Username: No username entered!')
  if password:
    print('Password: ', len(password) * '*')
  else:
    print('Password: No password entered!')
  print('\nAre they correct? (Y/n): ')
  response = input('')
  if response.strip().lower() == '' or response.strip().lower()[0] == 'y':
    print(sep)
    return (devices_file, username, password)
  else:
    print(sep)
    get_user_info()


def fetch_devices(fin):
  """

  Fetch device data from DEVICES_FILE, a .csv file

  Arguments:
    fin {String} -- relative file path of the input file

  Returns:
    devices {List | Boolean} -- List of dictionaries representing
                                hostname & IP address of each device
                                or False if error
  """
  try:
    # create list of dictionaries containing hostname & ip of each device
    devices = [row for row in csv.DictReader(open(fin))]
  except Exception as e:
    # report error if there is one
    print('There was a problem accessing the devices file...')
    print(e)
    devices = False
  # return devices
  return devices


def connect_to(hostname, ip, username, password):
  """

  Connect to device via SSH

  Arguments:
    hostname {String} -- Device Hostname
    ip {String} -- Device IP Address

  Returns:
    connection {Object | Boolean} -- Connection Handler or False if error
  """
  print('\n' + sep)
  print('    connecting to {0} on {1}'.format(hostname, ip))
  print(sep + '\n')
  # Device connection details
  device_dict = {
    'device_type': 'cisco_ios',
    'ip':  ip,
    'username': username,
    'password': password
  }
  # Try to connect
  try:
    # pass device details to netmiko connection handler
    connection = ConnectHandler(**device_dict)
    print('==> Connected')
  except Exception as e:
    result_dict[hostname] = 'Failure'
    print('==> Error connecting to {0}'.format(hostname))
    print('==> ' + str(e))
    connection = False
  return connection


def fetch_device_config(net_connect, hostname, data_file):
  """

  Fetch device configuration

  Arguments:
    net_connect {Object} -- Connection Handler
    hostname {String} -- Device Hostname
    data_file {String} -- Name of output data file

  No Returns
  """
  print('==> Fetching device configuration data...\n')
  sh_run = net_connect.send_command('show run')

  if sh_run:
    content = '\n' + sep + '\n' + hostname + '\n' + sep + '\n' + sh_run + '\n' + sep + '\n'
    # write config to file
    print('\n' + sep + '\n')
    print('==> Appending device configuration data to file...')
    append_data_to_file(data_file, content, hostname)
  else:
    print('\n' + sep + '\n')
    print('==> Configuration not fetched.')

def init_data_file_name():
  """

  Initialise data file

  No Arguments

  Returns:
    filename {String} -- data file name
  """
  now = datetime.datetime.now().isoformat().split('.')[0].replace(':', '-')
  filename = 'device-configs' + now + ".txt"
  return filename

def append_data_to_file(filename, data, hostname):
  """

  Write data to file file

  Arguments:
    fout {String} -- data file to be written to
    data {String} -- Device Configuration

  No Returns
  """
  print('==> Writing device configuration to file...')
  try:
    fout = open(filename, 'a')
    fout.write(data)
    print('==> Configuration written to:\n\n    {0}'.format(os.path.join(os.getcwd(), filename)))
    result_dict[hostname] = 'Success'
  except Exception as e:
    print('==> Error writing configuration to file...')
    print('==> ' + str(e))
    result_dict[hostname] = 'Failure'


def print_results():
  """

  Print(results table to stdout)

  No Arguments

  No Returns
  """
  print('\n' + sep + '\n')
  div = '    +' + ('-' * 22) + '+' +  ('-' * 22) + '+'
  print(div)
  print('    | {0:^20} | {1:^20} |'.format('Hostname', 'Status'))
  print(div)
  for hostname, status in result_dict.items():
    print('    | {0:^20} | {1:^20} |'.format(hostname, status))
  print(div + '\n')


def main():
  """

  Main function; fetch devices, connect to each in turn,
  fetch device config & write to file.

  Arguments:
    devices_file {String} -- Filename of devices file
    username {String} -- username for devices
    password {String} -- password for devices
  """
  (devices_file, username, password) = get_user_info()
  # fetch device data
  devices = fetch_devices(devices_file)
  # create new config file
  configs_file = init_data_file_name()
  # if device data fetched succesfully
  if devices:
    # loop through each device
    for device in devices:
      hostname = device['hostname']
      ip = device['ip']
      # connect to device
      net_connect = connect_to(hostname, ip, username, password)
      # if connection succesful
      if net_connect:
        # fetch device configs
        fetch_device_config(net_connect, hostname, configs_file)
    # once all devices have been looped over, print(results table)
    print_results()
  else:
    print('==> No devices available.')


if __name__ == "__main__":
    main()
