# EE495
# Hesham T. Banafa
# Jun 11th, 2022

from time import sleep
import requests


def poll(poll_url: str, data: dict, headers: dict) -> dict:
    res : requests.Response = \
        requests.post(poll_url, json=data, headers=headers)
    #print('sent ', data)
    print(res.text, res, res.reason)
    if res.status_code != 200: return None
    return res.json()
    
def emulate(poll_url, token_in: str):
    mac = "94:b9:7e:fb:57:1a"
    polling_interval_secons = 1
    polling_headers = {
        'accept' : 'application/json',
        'Content-Type': 'application/json' 
    }
    stop = False
    state = False
    while (not stop):
        sleep(polling_interval_secons)
        data = {
            'bluetooth_mac': mac,
            'state': state,
            'token': token_in
        }
        data_dict = poll(poll_url, data, polling_headers)
        if not data_dict: continue
        if data_dict['open_command']: state = True
        

if __name__ == '__main__':
    emulate("https://ibs.cronos.typedef.cf:4040/iotdevice/door/status", 
    "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJibHVldG9vdGhfbWFjIjoiOTQ6Yjk6N2U6ZmI6NTc6MWEifQ.oRbL0U70g8HGkKIOnwkesDiB40VWTPmwIWiysvP-hXA")