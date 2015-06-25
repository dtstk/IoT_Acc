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
    hum = ""
    temperature = ""
    movement = ""
    lux = ""

    print 'Number of arguments:', len(sys.argv), 'arguments.'
    print 'Argument List:', str(sys.argv)

    if len(sys.argv) != 2:
        print 'gw.py <data_to_parse>'
        sys.exit(2)

    json_data=open('config.json')
    config_data = json.load(json_data)
    json_data.close()

    temp =argv[0].split("_")
    print (temp)
    
    now_ = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    cfg = Configuration()
    cfg.cfgGWTime(config_data, now_)   
    
    if(temp[0] == "?"):
        #Registration
        handshakeId = temp[2]
        print handshakeId
       
        href = config_data["Server"]["url"] + 'api/Device/DeviceRegister'
        token = ComputeHash(now_, config_data["Server"]["key"])
        authentication = config_data["Server"]["id"] + ":" + token
        print(authentication)
        
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json', 'Timestamp': now_, 'Authentication': authentication}
        
        deviceDetail = {}
        deviceDetail["DeviceType"] = "Custom"
        deviceDetail["Name"] = "Arduino Nano " + handshakeId
    
        payload = {'Device': deviceDetail}
        print 'Request Content: {0}'.format(json.dumps(payload))
        r = requests.post(href, headers=headers, data=json.dumps(payload), verify=False)
    
        if r.status_code == 200:
           print 'Response Content: {0}'.format(r.content)
           data = json.loads(r.text)
           print 'Device Successfully Registered with ID={0}'.format(data['Device']['DeviceIdentifier'])
           print 'Device Handshake ID={0}'.format(handshakeId)
    
           config_data["Devices"][handshakeId]=data['Device']['DeviceIdentifier']
           print config_data
           json_data=open('config.json','w')
           json.dump(config_data, json_data)
           json_data.close()
    
           return data['Device']['DeviceIdentifier']
        else:
           print 'Error in setting time. Server response code: {0} {1}'.format(r.status_code, r.content)
           return '0'
    else:
        #Regular data message
        if temp[1] == "h":
            hum = temp[2]
            print "Hum: ", hum
        
        if temp[1] == "t":
            temperature = temp[2]
            print "Temp: ", temperature
    
        if temp[1] == "p":
            movement = temp[2]
            print "PIR: ", movement
    
        if temp[1] == "l":
            lux = temp[2]
            print "Lux: ", lux
    
        setAlarmState(config_data, now_, temperature, hum, lux, config_data["Devices"][temp[0]], movement)
    #    setAlarmState(config_data, now_, temperature, hum, lux, temp[0], movement)

def setAlarmState(config_data, now_, temper, humi, luxi, deviceId, move=0):    
    href = config_data["Server"]["url"] + 'api/events/process'
    token = ComputeHash(now_, config_data["Server"]["key"])
    authentication = config_data["Server"]["id"] + ":" + token
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
    r = requests.post(href, headers=headers, data=json.dumps(payload), verify=False)
    print (r)

def ComputeHash(timeStamp, key):
    message = bytes(timeStamp).encode('utf-8')
    secret  = bytes(key).encode('utf-8')
    signature = base64.b64encode(hmac.new(message, secret, digestmod=hashlib.sha256).digest())
    print (signature)
    return signature


if __name__ == '__main__':
    main(sys.argv[1:])
