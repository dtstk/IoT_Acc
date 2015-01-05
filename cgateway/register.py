#!/usr/bin/python

import os
import sys, getopt
import json
import requests

import hashlib
import hmac
import base64
import serial
from decimal import *
from time import gmtime, strftime
from datetime import datetime

url = 'http://officeauthomationservice.cloudapp.net/'
key = 'QG4WK-X8EGS-NA4UJ-Z4YTC'
companyId = '1'

class Configuration():
    def __init__(self):
        self.id = ""
        self.timeFromServer = ""
    def cfgGWTime(self, now_):
        href = url + 'API/Device/DeviceRegister'
        token = ComputeHash(now_, key)
        authentication = companyId + ":" + token
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json', 'Authentication': authentication}
        r = requests.get(href, headers=headers)
        if r.status_code == 200:
            self.timeFromServer = r.json()
            print ("Setting up time to: " + self.timeFromServer)
            self.command = 'sudo -S date -s "' + self.timeFromServer + '"'
            os.popen(self.command, 'w').write("123")
        else:
            print 'Error in setting time. Server response code: %i' % r.status_code       

def main(argv):
    hum = ""
    temperature = ""
    movement = ""
    lux = ""

    print 'Number of arguments:', len(sys.argv), 'arguments.'
    print 'Argument List:', str(sys.argv)

    if len(sys.argv) != 2:
        print 'register.py <data_to_parse>'
        sys.exit(2)

    now_ = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    cfg = Configuration()
    cfg.cfgGWTime(now_)

    temp =argv[0].split("_")
    print (temp)

    fromType = list(temp[0])
    print fromType
    print fromType[2]
   
    href = url + 'api/events/process'
    token = ComputeHash(now_, key)
    authentication = companyId + ":" + token
    print(authentication)
    
    headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json', 'Timestamp': now_, 'Authentication': authentication}
    
    devices = []    

    deviceDetail = {}
    deviceDetail["DeviceType"] = "Custom"
    deviceDetail["Name"] = "Arduino Nano"
    devices.append(temp)

    print devices

    payload = {'Device': devices}
    print(json.dumps(payload))
    r = requests.post(href, headers=headers, data=json.dumps(payload))
    print (r)

def ComputeHash(timeStamp, key):
    message = bytes(timeStamp).encode('utf-8')
    secret  = bytes(key).encode('utf-8')
    signature = base64.b64encode(hmac.new(message, secret, digestmod=hashlib.sha256).digest())
    print (signature)
    return signature


if __name__ == '__main__':
    main(sys.argv[1:])
