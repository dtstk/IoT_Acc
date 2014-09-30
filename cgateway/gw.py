#!/usr/bin/python

import os
import sys, getopt
import time
import json
import requests

import hashlib
import hmac
import base64
import serial
from decimal import *

def main(argv):
    url = 'http://officeauthomationservice.cloudapp.net/'
    # now = '2014-08-13T14:06:50.7214802+03:00'
    # ser = serial.Serial(5)
    hum = ""
    temperature = ""
    movement = ""
    print 'Number of arguments:', len(sys.argv), 'arguments.'
    print 'Argument List:', str(sys.argv)

    if len(sys.argv) != 2:
        print 'gw.py <data_to_parse>'
        sys.exit(2)

    # print ser.name
    now = time.strftime("%c")
    # line = ser.readline()
    temp =argv[0].split("_")
    print (temp)

    if temp[0] == "Dh":
        temperature, hum = processDHTSensor(temp, len(temp))
    
    print temperature, hum

    setAlarmState(now, url, temperature, hum, movement)

def processDHTSensor(data, dataLen):
    #sensors = data[].split("_")
    for sensor in data:
        print "sensor:", sensor
        #sensor_data = sensor.split("|")
        #print sensor_data
        temper = data[3]
        hum = data[2]
        '''
        if sensor_data[0] == '1':
            #it is Due with temp and hum
            temperature = sensor_data[1]
            hum = sensor_data[2]
            #print "temperature", temperature
        if sensor_data[0] == '2':
            #it is UNO with PIR
            movement = sensor_data[1]
        '''
    return temper, hum


def setAlarmState(now, url, temper, humi, move=0):
    href = url + 'api/events/process'
    companyId = '1'
    key = 'QG4WK-X8EGS-NA4UJ-Z4YTC'
    token = ComputeHash(now, key)
    authentication = companyId + ":" + token
    print(authentication)
    headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json', 'Timestamp': now, 'Authentication': authentication}
    measurements = []    
    if temper != "":
        temp = {}
        temp["EventType"] = 1
        temp["EventValue"] = int(temper)
        temp["EventTime"] = now
        measurements.append(temp)

    if humi != "":
        hum = {}
        hum["EventType"] = 2
        hum["EventValue"] = int(humi)
        hum["EventTime"] = now
        measurements.append(hum)

    if move != "":
        movement = {}
        movement["EventType"] = 7
        movement["EventValue"] = int(move)
        movement["EventTime"] = now
        measurements.append(movement)
       
    #measurements = [{"EventType":7,"EventValue":temp,"EventTime":now},{"EventType":6,"EventValue":hum,"EventTime":now},{"EventType":1,"EventValue":movement,"EventTime":now}]

    print measurements
    #return 1

    payload = {'events': measurements, "deviceId": 3}
    print(json.dumps(payload))
    r = requests.post(href, headers=headers, data=json.dumps(payload))
    print (r)
    #print (r.json())

def ComputeHash(timeStamp, key):
    message = bytes(timeStamp).encode('utf-8')
    secret  = bytes(key).encode('utf-8')
    signature = base64.b64encode(hmac.new(message, secret, digestmod=hashlib.sha256).digest())
    print (signature)
    return signature


if __name__ == '__main__':
    main(sys.argv[1:])
