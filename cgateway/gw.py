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
ids = {'D': 3, 'N': 9, 'M': 4, 'U': 6}

class Configuration():
    def __init__(self):
        self.id = ""
        self.timeFromServer = ""
    def cfgGWTime(self, now_):
        href = url + 'API/Device/GetServerDateTime'
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
        print 'gw.py <data_to_parse>'
        sys.exit(2)

    now_ = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    cfg = Configuration()
    cfg.cfgGWTime(now_)

    temp =argv[0].split("_")
    print (temp)

    fromType = list(temp[0])
    print fromType
   
    if fromType[1] == "h":
        hum = processDHTSensor(temp, len(temp))
        print temperature, hum
    
    if fromType[1] == "t":
        temperature = processDHTSensor(temp, len(temp))
        print temperature

    if fromType[1] == "p":
        movement = processPIRSensor(temp, len(temp))
        print "movement: ", movement

    if fromType[1] == "l":
        lux = processLuxSensor(temp, len(temp))
        print "Lux: ", lux

    setAlarmState(now_, temperature, hum, lux, ids[fromType[0]], movement)

def processPIRSensor(data, dataLen):
    for sensor in data:
        print "sensor: ", sensor
        move = data[1]
    return move

def processLuxSensor(data, dataLen):
    for sensor in data:
        print "sensor: ", sensor
        lux = data[1]
    return lux

def processDHTSensor(data, dataLen):
    for sensor in data:
        print "sensor:", sensor
        retData = data[1]
    return retData

def setAlarmState(now_, temper, humi, luxi, deviceId, move=0):    
    href = url + 'api/events/process'
    token = ComputeHash(now_, key)
    authentication = companyId + ":" + token
    print(authentication)
    
    headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json', 'Timestamp': now_, 'Authentication': authentication}
    measurements = []    
    if temper != "":
        temp = {}
        temp["EventType"] = 1
        temp["EventValue"] = int(temper)
        temp["EventTime"] = now_
        measurements.append(temp)

    if humi != "":
        hum = {}
        hum["EventType"] = 2
        hum["EventValue"] = int(humi)
        hum["EventTime"] = now_
        measurements.append(hum)

    if move != "":
        movement = {}
        movement["EventType"] = 7
        movement["EventValue"] = int(move)
        movement["EventTime"] = now_
        measurements.append(movement)

    if luxi != "":
        lux = {}
        lux["EventType"] = 6
        lux["EventValue"] = int(luxi)
        lux["EventTime"] = now_
        measurements.append(lux)
       
    #measurements = [{"EventType":7,"EventValue":temp,"EventTime":now_},{"EventType":6,"EventValue":hum,"EventTime":now_},{"EventType":1,"EventValue":movement,"EventTime":now_}]

    print measurements

    payload = {'events': measurements, "deviceId": deviceId}
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
