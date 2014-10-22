import os
import sys
import time
import json
import requests

import hashlib
import hmac
import base64

def main():
    url = 'http://officeauthomationservice.cloudapp.net/'
    now = time.strftime("%c")
    #now = '2014-08-13T14:06:50.7214802+03:00'
    setAlarmState(now, url)

def setAlarmState(now, url):
    href = url + 'api/events/process'
    companyId = '1'
    key = 'QG4WK-X8EGS-NA4UJ-Z4YTC'
    token = ComputeHash(now, key)
    authentication = companyId + ":" + token
    print authentication
    headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json', 'Timestamp': now, 'Authentication': authentication}
    measurements = [{"EventType":7,"EventValue":1.0,"EventTime":"2014-08-13T14:06:50.4121575+03:00"},{"EventType":6,"EventValue":400.0,"EventTime":"2014-08-13T14:06:50.4131567+03:00"},{"EventType":1,"EventValue":27.45,"EventTime":"2014-08-13T14:06:50.4131567+03:00"}]
    payload = [{'events': measurements, "deviceId": 3}]
    print json.dumps(payload[0])
    r = requests.post(href, headers=headers, data=json.dumps(payload))
    print r
    print r.json()

def ComputeHash(timeStamp, key):
    message = bytes(timeStamp).encode('utf-8')
    secret  = bytes(key).encode('utf-8')
    signature = base64.b64encode(hmac.new(message, secret, digestmod=hashlib.sha256).digest())
    print signature
    return signature


if __name__ == '__main__':
    main()
