import sys
from azure.servicebus import ServiceBusService, Message, Queue
#from .classes import config_parser
#import classes.config_parser

def main(argv):
    print 'Starting program...'

    queue_name =argv[0]
    print (queue_name)
    
#   config = ConfigParser()
    bus_service = ServiceBusService( service_namespace='rdciot', shared_access_key_name='RootManageSharedAccessKey', shared_access_key_value='EXeZe7r49jCoDz79fESxtMdXwYU6iQwG1Gbo8J4HXyY=')
    print bus_service
    
    while True:
        msg = bus_service.receive_queue_message(queue_name, peek_lock=False)
        print(msg.body)
    
    
    print 'Program finished.'

if __name__ == '__main__':
    main(sys.argv[1:])
