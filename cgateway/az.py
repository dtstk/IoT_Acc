#!/usr/bin/python
import sys
import json
from azure.servicebus import ServiceBusService, Message, Queue

def main(argv):
    print 'Starting program...'

    internalDeviceId = argv[0]
    json_data=open('config.json')
    config_data = json.load(json_data)
    json_data.close()

    externalDeviceId = config_data["Devices"][internalDeviceId]
    queue_name = 'custom_' + config_data["Server"]["id"] + '_' + config_data["Server"]["Deviceid"] + '_' + externalDeviceId
    print (queue_name)
    
    bus_service = ServiceBusService( service_namespace='rdciot', shared_access_key_name='RootManageSharedAccessKey', shared_access_key_value='EXeZe7r49jCoDz79fESxtMdXwYU6iQwG1Gbo8J4HXyY=')
    print bus_service
    
    while True:
        msg = bus_service.receive_queue_message(queue_name, peek_lock=False)
        print(msg.body)
    
    
    print 'Program finished.'

if __name__ == '__main__':
    main(sys.argv[1:])
