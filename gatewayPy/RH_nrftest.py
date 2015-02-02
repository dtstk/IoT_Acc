#!/usr/bin/env python3
#This is main function that implements communication with NRF24l01+ modules on Raspberry Pi

import select
import threading
from nrf24l01 import *
from random import randint
from gw import *
from quick2wire.gpio import pins, In, Out, Rising, Falling, Both, pi_broadcom_soc
from threading import Thread

def handleInterrup():    
    epoll = select.epoll()
    with pin1:
        epoll.register(pin1,select.EPOLLIN | select.EPOLLET)
        print("")
        while True:
            events = epoll.poll()
            for fileno, event in events:
                if fileno == pin1.fileno():
                    handle_pin_1() #ISR for GPIO interrupt

def handle_pin_1():
    print("Interrupt on GPIO has occured")
    
#define global variables - used across threads
SendObj = NRF24() #Start class  
pin1 = pins.pin(5,direction=In,interrupt=Rising) #define GPIO 18?? pin for interrupt

       
if __name__ == "__main__":    
    #pin1 = pins.pin(5,direction=In,interrupt=Rising) #define GPIO 18?? pin for interrupt
    #epoll = select.epoll()
    #print("Starting threads")
 
    t1 = Thread(target = handleInterrup)
    t1.start()
    
        
      									        
    rxtx = input("Input option: \n\rrx - receive\n\rtx - transmit\n\rr0 - MASTER\n\r")
    try:
        if rxtx == 'tx':
            print("Starting Transmitter..\n")
            SendObj.init() #OK
            #SendObj.setModeTx
            #av = SendObj.available() SendObj.sendData("hello world")
            SendObj.send2("Hello world ;)")
            #print(SendObj.readReg(FIFO_STATUS))
            SendObj.setModeTx()
            if not(SendObj.waitPacketSent()):
                print("Send SUCCESSFUL")
            SendObj.radio_pin.value = 0
            SendObj.closeCEpin()
        elif rxtx == 'r0':
            """Code example that is working with MIRF based Arduino sensor node"""
            print("Starting Mirf MASTER")
            
            #SendObj.initNRF24()            
            SendObj.initForMirf()
            SendObj._thisAddress = 1; #MASTER node ID
            SendObj.setRXAddress(0,'cln1')
            SendObj.setRXAddress(1,'serv')
            SendObj.setTXAddress('cln1')
            SendObj.setModeRx() 
            #SendObj.printRegisterMap()
            while(1):
                SendObj.setModeRx()
                if SendObj.available(COMMAND_R_RX_PAYLOAD):
                     # TODO: Should call further action in other the thread.
                     print("Got message!", end="\n\r")
                     message = SendObj.rcvAllPacket()
                     sAddres = message[0]
                     s1Reading = message[1]
                     s2Reading = message[2]
                     s3Reading = message[3]
                     s4Reading = message[4]
                     print ("Sensor ID",sAddres," received data \n\rS1: ",s1Reading," \n\rS2: ",s2Reading," \n\rS3: ",s3Reading," \n\rS4: ",s4Reading)
                     #print(message)
                     SendObj.clearRxBuf()
                     SendObj.flushRx()
                     SendObj.setRXAddress(0,'cln1')
                     SendObj.setTXAddress("cln1")
                     delay = randint(10,100) #new delay for receiver MAC
                     print("New delay: ",delay,end="\n\r")
                     SendObj.setModeTx()
                     SendObj.setPacket(BROADCAST_ADDRESS,delay,100,200,250)
                     #SendObj.printRegisterMap()
                     SendObj.sendMIRF()
                     if (SendObj.waitPacketSent()):
                         print("Send SUCCESSFUL\n\n\r")
        elif rxtx == 'rx':
            print("Starting Receiver..")
            print("Sending hello message")
            SendObj.init()
            SendObj.send2("Hello world ;)")
            #print(SendObj.readReg(FIFO_STATUS)) #0x17
            SendObj.setModeTx()
            if not(SendObj.waitPacketSent()):
                print("Send SUCCESSFUL\n")
            
            SendObj.setModeRx()
            print("Listening for reply")
            while(1):
                #SendObj.setModeRx()
                if (SendObj.available(COMMAND_R_RX_PAYLOAD)): 
                     print("Got message: ", end="")
                     message = SendObj.rcv()
                     print(message)
                     SendObj.clearRxBuf()
                     SendObj.flushRx()
                     #SendObj.clearRxTx()
                     SendObj.send2("And hello back to you")
                     SendObj.waitPacketSent()
                     print("Sent a reply")
                     #SendObj.setModeRx()
                else:
                     time.sleep(0.01)
                     print(".",end=""),
            SendObj._radio_pin.value = 0
            SendObj.closeCEpin()
        elif rxtx == 't':
            SendObj.initNRF24()
            SendObj._thisAddress = 1;
            SendObj.setRXAddress(0,'cln1')
            SendObj.setRXAddress(1,'serv')
            SendObj.setTXAddress('cln1')
            
            SendObj.printRegisterMap()
            SendObj._radio_pin.value = 0
            SendObj.closeCEpin()
        elif rxtx == 'm':
            main(['Dh_20_Dt_30_Up_40',30])
            
    except(KeyboardInterrupt,SystemExit): #If ctrl+c breaks operation or system shutdown; no Traceback is shown
        SendObj._radio_pin.value = 0
        SendObj._radio_pin.close() #First close the CE-pin, so that it can be opened again without error!        
        pin1.close()
        t1._stop()#stop thread t1
        print("\n\nKeyboard Interrupt => GPIO-PIN closed!\n")                    
        pass #continue to break or shutdown! hodes traceback
    except Exception: #in case of other errors closes CE pin and shows error message
        SendObj._radio_pin.value = 0
        SendObj._radio_pin.close() #First close the CE-pin, so that it can be opened again without error!
        pin1.close()
        t1._stop()#stop thread t1
        print("\n\nOther ERRO => GPIO-PIN closed!\n")
        raise#pass
    
    		    
    

