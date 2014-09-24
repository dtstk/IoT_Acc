import os
import sys
import time
import json
import requests

import hashlib
import hmac
import base64
import serial

def main():
    url = 'http://officeauthomationservice.cloudapp.net/'
    #now = '2014-08-13T14:06:50.7214802+03:00'
    ser = serial.Serial(5)
    hum = ""
    temperature = ""
    movement = ""

    print ser.name
    while True:
        now = time.strftime("%c")
        line = ser.readline()
        temp = line.split(":")
        if temp[0] == "msg":
            print (line)
            sensors = temp[1].split("_")
            for sensor in sensors:
                print "sensor:", sensor
                sensor_data = sensor.split("|")
                #print sensor_data
                if sensor_data[0] == '1':
                    #it is Due with temp and hum
                    temperature = sensor_data[1]
                    hum = sensor_data[2]
                    #print "temperature", temperature
                if sensor_data[0] == '2':
                    #it is UNO with PIR
                    movement = sensor_data[1]
            print "."
            #print temperature, hum, movement
            setAlarmState(now, url, temperature, hum, movement)

def setAlarmState(now, url, temp, hum, movement):
    href = url + 'api/events/process'
    companyId = '1'
    key = 'QG4WK-X8EGS-NA4UJ-Z4YTC'
    token = ComputeHash(now, key)
    authentication = companyId + ":" + token
    print(authentication)
    headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json', 'Timestamp': now, 'Authentication': authentication}
    measurements = [{"EventType":7,"EventValue":temp,"EventTime":now},{"EventType":6,"EventValue":hum,"EventTime":now},{"EventType":1,"EventValue":movement,"EventTime":now}]
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
    main()