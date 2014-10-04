#!/usr/bin/env python3
#This is main function that implements comunication with NRF24l01+ modules on Raspbery Pi


from nrf24l01 import *

if __name__ == "__main__":
    rxtx = input("Input option: \n\rrx - receive\n\rtx - transmit\n\rr0 - receive from Mirf\n")
    SendObj = RH_NRF24() #Start class
    try:
        if rxtx == 'tx':
            print("Starting Transmiter..\n")
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
            print("Starting Receiver on Pipe 0..")
            
            SendObj.initForMirf()
            SendObj._thisAddress = 1; #MASTER node ID
            
            #SendObj.setModeRx()
            #Print register map
            #SendObj.printRegisterMap()
 
            
            while(1):
                SendObj.setModeRx()
                if SendObj.available(COMMAND_R_RX_PAYLOAD):
                     print("Got message: ", end="")
                     message = SendObj.rcvMRFI()
                     print(message)
                     SendObj.clearRxBuf()
                     SendObj.flushRx()
                     SendObj.setRXAddress(0,'cln1')
                     SendObj.setTXAddress("cln1")
                     SendObj.setModeTx()
                     #SendObj.printRegisterMap()
                     SendObj.sendMIRF(100)
                     if not(SendObj.waitPacketSent()):
                         print("Send SUCCESSFUL")
        elif rxtx == 't0':
            SendObj.initForMIrfTx()
            SendObj.send2('1234')
            SendObj.setModeTx()
            if not(SendObj.waitPacketSent()):
                print("Send SUCCESSFUL")
            SendObj.radio_pin.value = 0
            SendObj.closeCEpin()
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
            SendObj.radio_pin.value = 0
            SendObj.closeCEpin()
            
    except(KeyboardInterrupt,SystemExit): #If ctrl+c breaks operation or system shutdown; no Traceback is shown
        SendObj.radio_pin.value = 0
        SendObj.radio_pin.close() #First close the CE-pin, so that it can be opened again without error!
        print("\n\nKeyboard Interrup => GPIO-PIN closed!\n")                    
        pass #continue to break or shutdown! hodes traceback
    except Exception: #in case of other errors closes CE pin and shows error message
        SendObj.radio_pin.value = 0
        SendObj.radio_pin.close() #First close the CE-pin, so that it can be opened again without error!
        print("\n\nOther ERRO => GPIO-PIN closed!\n")
        raise#pass
        
    
     
