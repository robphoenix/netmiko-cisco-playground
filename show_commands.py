import csv
import os
import getpass
import datetime
from netmiko import ConnectHandler


# visual separator
sep = '=' * 70


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
  command = input('Read only command to be applied: ')
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
  if command:
    print('Command: ', command)
  else:
    print('Command: No command entered!')
  print('\nAre they correct? (Y/n): ')
  response = input('')
  if response.strip().lower() == '' or response.strip().lower()[0] == 'y':
    print(sep)
    return (devices_file, username, password, command)
  else:
    print(sep)
    get_user_info()


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


def connect_to(hostname, ip, username, password):
  """

  Connects to device

  Arguments:
    hostname {String} -- Device Hostname
    ip {String} -- Device IP Address

  Returns:
    Object | Boolean -- Connection Handler or False
  """
  print('\n' + sep)
  print('    connecting to {0} on {1}'.format(hostname, ip))
  print(sep + '\n')
  # Device connection details
  device_dict = {
  'device_type': 'cisco_ios',
  'ip':  ip,
  'username': username,
  'password': password,
  }
  # Try to connect
  try:
    connection = ConnectHandler(**device_dict)
    print('==> Connected')
    print('\n' + sep)
    # print('==> Sending commands...')
    # print(sep)
    # apply the command
    # command = connection.send_command('ter len 0')
    # print('\n' + sep)
    # print('ter len 0: ', command)
    # command = connection.send_command(command)
    # print('\n' + sep)
    # print('Command output: \n', command)
    # print('\n' + sep + '\n')
    # print('==> Exiting...')
    return connection
  except Exception as e:
    print('==> Error connecting to {0}'.format(hostname))
    print('==> ' + str(e))
    return False


def show_commands(net_connect, hostname, password, command, data_file):
  """

  Applies given commands to device

  Arguments:
    net_connect {Object} -- Connection Handler
    hostname {String} -- Device Hostname
    command {String} -- Command to apply
  """
  # check if in enable mode
  print('\n' + sep)
  print('==> Sending commands...')
  print(sep)
  # apply the command
  res = net_connect.send_command(command)
  print('\n' + sep)
  print(res)
  print('\n' + sep + '\n')
  # write config to file
  print('\n' + sep + '\n')
  print('==> Appending command output data to file...')
  content = '\n' + sep + '\n' + hostname + ' : '+ command + '\n' + sep + '\n' + res + '\n' + sep + '\n'
  append_data_to_file(data_file, content, hostname)
  print('==> Exiting...')


def init_data_file_name():
  """

  Initialise data file

  No Arguments

  Returns:
    filename {String} -- data file name
  """
  now = datetime.datetime.now().isoformat().split('.')[0].replace(':', '-')
  filename = 'show-commands-' + now + ".txt"
  return filename


def append_data_to_file(filename, data, hostname):
  """

  Write data to file file

  Arguments:
    fout {String} -- data file to be written to
    data {String} -- Device Configuration

  No Returns
  """
  print('==> Writing command output to file...')
  try:
    fout = open(filename, 'a')
    fout.write(data)
    print('==> Command output written to:\n\n    {0}'.format(os.path.join(os.getcwd(), filename)))
  except Exception as e:
    print('==> Error writing configuration to file...')
    print('==> ' + str(e))


def main():
  res = get_user_info()
  (devices_file, username, password, command) = res
  data_file = init_data_file_name()
  # fetch device data
  devices = fetch_devices(devices_file)
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
        show_commands(net_connect, hostname, password, command, data_file)
  else:
    print('==> No devices available.')


if __name__ == "__main__":
    main()
