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

class Configuration():
    def __init__(self):
        self.id = ""
        self.timeFromServer = ""
    def cfgGWTime(self, config_data, now_):
        href = config_data["Server"]["url"] + 'API/Device/GetServerDateTime'
        token = ComputeHash(now_, config_data["Server"]["key"])
        authentication = config_data["Server"]["id"] + ":" + token
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json', 'Authentication': authentication}
        r = requests.get(href, headers=headers, verify=False)
        if r.status_code == 200:
            self.timeFromServer = r.json()
            print ("Setting up time to: " + self.timeFromServer)
            self.command = 'sudo -S date -s "' + self.timeFromServer + '"'
            os.popen(self.command, 'w').write("123")
        else:
            print 'Error in setting time. Server response code: %i' % r.status_code       

def main(argv):

    print 'Sync PI and server time'       

    json_data=open('config.json')
    config_data = json.load(json_data)
    json_data.close()

    now_ = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    cfg = Configuration()
    cfg.cfgGWTime(config_data, now_)   

def ComputeHash(timeStamp, key):
    message = bytes(timeStamp).encode('utf-8')
    secret  = bytes(key).encode('utf-8')
    signature = base64.b64encode(hmac.new(message, secret, digestmod=hashlib.sha256).digest())
    print (signature)
    return signature

if __name__ == '__main__':
    main(sys.argv[1:])
