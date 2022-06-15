# Quick enroll new device
# Hesham T. Banafa
# Jun 12th, 2022

from decouple import config
import requests

# idk if this stays in memory...
headers = {
  "accept": "application/json",
  "Content-type": "application/json"
}
def main():

    if len(sys.argv) != 4:
        print_help()
        exit(1)

    device_type = sys.argv[1]
    bluetooth_mac = sys.argv[2]
    description = sys.argv[3]
    if device_type == 'DOOR':
        mkdoor(bluetooth_mac, description)
    elif device_type == 'MONITOR':
        mkmonitor(bluetooth_mac, description)
    else:
        print('Device type not DOOR or MONITOR', file=sys.stderr)
        exit(1)
    # gen print token of bluetooth_mac
    print(create_iot_dev_token(bluetooth_mac))

def mkdoor(bluetooth_mac: str, description: str):
   data = {
       "bluetooth_mac": bluetooth_mac,
       "description": description
    }

    #response = requests.post("")

def mkmonitor(bluetooth_mac: str, description: str):
   pass

def print_help():
    msg = 'usgae: enroll_iotdevice <DOOR|MONITOR> <bluetooth_mac> <description>'
    print(msg)