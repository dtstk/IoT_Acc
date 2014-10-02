#!/usr/bin/env python3
from quick2wire.spi import * 
from quick2wire.gpio import Pin 
from quick2wire.gpio import In,Out,pi_header_1 
import time 

PAYLOAD_SIZE = 3 
NRF24_MAX_PAYLOAD_LEN = 32 
NRF24_HEADER_LEN = 4 
NRF24_MAX_MESSAGE_LEN = NRF24_MAX_PAYLOAD_LEN - NRF24_HEADER_LEN 
SMALL_PAUSE = 0 
LONG_PAUSE=0
 
DataRate1Mbps = 0 
DataRate2Mbps = 2 
DataRate250kbps = 4
 
#Define settings variables for nRF:
SET_ACK = 0x01 #Auto ack on (EN_AA) 
SET_ACK_RETR = 0x2F #15 retries, 750us paus in between in auto ack (SETUP_RETR) 
SET_DATAPIPE = 0x01 #Datapipe 0 is used (EN_RXADDR) 
SET_ADR_WIDTH = 0x03 #5 byte address (SETUP_AW) 
SET_FREQ = 0x01 #2,401GHz (RF_CH) 
SET_SETUP = 0x07 #1Mbps, -0dB, (250kbps = 0x27) (RF_SETUP) 
ADDRESS = 0x12 
BROADCAST_ADDRESS = 0xFF
SET_RX_ADDR_P0 = [ADDRESS,ADDRESS,ADDRESS,ADDRESS,ADDRESS] #Receiver address( RX_ADDR_P0) 
SET_TX_ADDR = [ADDRESS,ADDRESS,ADDRESS,ADDRESS,ADDRESS] #Transmitter address (TX_ADDR)
SET_PAYLOAD_S = 0x03 #3byte payload size (32byte = 0x20)(RX_PW_P0) 
SET_CONFIG = 0x1E #1=mask_MAX_RT (IRQ-vector), E=transmitter, F= Receiver (CONFIG)
#STATUS
RH_NRF24_RX_DR = 0x40 
RH_NRF24_TX_DS = 0x20 
RH_NRF24_MAX_RT = 0x10 
RH_NRF24_RX_P_NO = 0x0e 
RH_NRF24_STATUS_TX_FULL = 0x01
#define DYNPD 0x1c
RH_NRF24_DPL_ALL = 0x2f 
RH_NRF24_DPL_P5 = 0x20 
RH_NRF24_DPL_P4 = 0x10 
RH_NRF24_DPL_P3 = 0x08 
RH_NRF24_DPL_P2 = 0x04 
RH_NRF24_DPL_P1 = 0x02 
RH_NRF24_DPL_P0 = 0x01

#define RH_NRF24_REG_1D_FEATURE 0x1d
RH_NRF24_EN_DPL = 0x04 
RH_NRF24_EN_ACK_PAY = 0x02 
RH_NRF24_EN_DYN_ACK = 0x01

#define RH_NRF24_REG_05_RF_CH 0x05
NRF24_RF_CH = 0x7F

#define RH_NRF24_REG_06_RF_SETUP 0x06
NRF24_CONT_WAVE = 0x80 
NRF24_RF_DR_LOW = 0x20 
NRF24_PLL_LOCK = 0x10 
NRF24_RF_DR_HIGH = 0x08 
NRF24_PWR = 0x06 
NRF24_PWR_m18dBm = 0x00 
NRF24_PWR_m12dBm = 0x02 
NRF24_PWR_m6dBm = 0x04 
NRF24_PWR_0dBm = 0x06
 
#define RH_NRF24_REG_00_CONFIG 0x00
NRF24_MASK_RX_DR = 0x40 
NRF24_MASK_TX_DS = 0x20 
NRF24_MASK_MAX_RT = 0x10 
NRF24_EN_CRC = 0x08 
NRF24_CRCO = 0x04 
NRF24_PWR_UP = 0x02 
NRF24_PRIM_RX = 0x01

#define RH_NRF24_REG_07_STATUS 0x07
NRF24_RX_DR = 0x40 
NRF24_TX_DS = 0x20 
NRF24_MAX_RT = 0x10 
NRF24_RX_P_NO = 0x0e 
NRF24_STATUS_TX_FULL = 0x01

#define RH_NRF24_REG_17_FIFO_STATUS 0x17
NRF24_TX_REUSE = 0x40 
NRF24_TX_FULL = 0x20 
NRF24_TX_EMPTY = 0x10 
NRF24_RX_FULL = 0x02 
NRF24_RX_EMPTY = 0x01

#nRF registers:
CONFIG = 0x00 
EN_AA = 0x01 
EN_RXADDR = 0x02 
SETUP_AW = 0x03 
SETUP_RETR = 0x04 
RF_CH = 0x05 
RF_SETUP = 0x06 
STATUS = 0x07 
OBSERVE_TX = 0x08 
CD = 0x09 
RX_ADDR_P0 = 0x0A 
RX_ADDR_P1 = 0x0B 
RX_ADDR_P2 = 0x0C 
RX_ADDR_P3 = 0x0D 
RX_ADDR_P4 = 0x0E 
RX_ADDR_P5 = 0x0F 
TX_ADDR = 0x10 
RX_PW_P0 = 0x11 
RX_PW_P1 = 0x12 
RX_PW_P2 = 0x13 
RX_PW_P3 = 0x14 
RX_PW_P4 = 0x15 
RX_PW_P5 = 0x16 
FIFO_STATUS = 0x17 
DYNPD = 0x1C 
FEATURE = 0x1D
 
READ_REG = 0x00 
WRITE_REG = 0x20 
RESET_STATUS = 0x70
 
WR_TX_PLOAD = 0xA0 
RD_RX_PLOAD = 0x61
 
#SPI Command names
COMMAND_R_REGISTER = 0x00 
COMMAND_W_REGISTER = 0x20 
COMMAND_ACTIVATE = 0x50 #// only on RFM73 ? 
COMMAND_R_RX_PAYLOAD = 0x61 
COMMAND_W_TX_PAYLOAD = 0xa0 
COMMAND_FLUSH_TX = 0xe1 
COMMAND_FLUSH_RX = 0xe2 
COMMAND_REUSE_TX_PL = 0xe3 
COMMAND_R_RX_PL_WID = 0x60 
def COMMAND_W_ACK_PAYLOAD(self,pipe): 
    return (0xa8|(pipe&0x7)) 
    
COMMAND_W_TX_PAYLOAD_NOACK = 0xb0 
COMMAND_NOP = 0xff 

class RH_NRF24:
    ''' Class implementing all communication with NRF24L01P'''
    def __init__(self):
        """__init__ function is allways run first, when the class is called!"""
        self.nrf24SPI = SPIDevice(0, 0) #Define SPI-unit (used in doOperation)
        self.radio_pin = pi_header_1.pin(22, direction=Out) #"CE" on nRF, output
        self.radio_pin.open()
        self._mode = -1
        self.RHModeIdle = 0
        self.RHModeRX = 1
        self.RHModeTX = 2
        self._rxBufValid = 0
        self.TransmitPower18dBm = 0
        self.TransmitPower12dBm = 1
        self.TransmitPower6dBm = 2
        self.TransmitPower0dBm = 3
        self.DataRate1Mbps = 0
        self.DataRate2Mbps = 1
        self.DataRate250kbps = 2
        self._buf = "qwe"#[None]* NRF24_MAX_PAYLOAD_LEN
        self._txHeaderTo = 0xFF
        self._txHeaderFrom = 0xFF
        self._txHeaderId = 0x00
        self._txHeaderFlags = 0x00
        self._thisAddress = 0xff
        self._rxGood=0
        
        self._configuration = NRF24_EN_CRC | NRF24_CRCO
        self._chipEnablePin = 22
        
        #related to ACCENTURE application
        self._basicPacket = []
        self._nodeID = 44
    
    def setRF(self,data_rate,power):
        _value = (power << 1) & NRF24_PWR #if DR = 1Mbps
        #print (data_rate)
        if data_rate == self.DataRate250kbps:
            _value |= NRF24_RF_DR_LOW
        #    print("Set 250kbps")
        elif data_rate == self.DataRate2Mbps:
            _value |= NRF24_RF_DR_HIGH
        #    print("Set 2Mbps") else: print("Set 1Mbps") print (_value)
        self.writeReg(RF_SETUP,_value)
        return True
    
    def flushTx(self):
        self.writeTopReg(COMMAND_FLUSH_TX)
    
    def flushRx(self):
        self.writeTopReg(COMMAND_FLUSH_RX)
        
    def setChannel(self,channel):
        #Setup Freq
        self.writeReg(RF_CH,channel & NRF24_RF_CH)
        return True
    
    def setModeIdle(self):
        if (self._mode != self.RHModeIdle):
            self.writeReg(CONFIG,self._configuration)
            self.radio_pin.value = 0
            self._mode = self.RHModeIdle
    
    def setModeRx(self):
        if self._mode != self.RHModeRX:
            self.writeReg(CONFIG,self._configuration | NRF24_PWR_UP | NRF24_PRIM_RX)
        self.radio_pin.value=1
        self._mode = self.RHModeRX
        
    def setModeTx(self):
        if self._mode != self.RHModeTX:
            self.radio_pin.value = 0
            self.writeReg(CONFIG,self._configuration | NRF24_PWR_UP)
            self.radio_pin.value = 1
            self._mode = self.RHModeTX
    
    def writeReg(self,register,value):
        bytes = [WRITE_REG|register]
        bytes.append(value)
        return self.doOperation(writing(bytes))
    
    #def spiTransfer(self,value)
    #    return self.doOperation(writing(value))
        
    def writeTopReg(self,register):
        bytes = [register]
        return self.doOperation(writing(bytes))
        
    def doOperation(self,operation):
        """Do one SPI operation"""
        time.sleep(SMALL_PAUSE) #Make sure the nrf is ready
        #print("operation: ")
        #print(operation)
        toReturn = self.nrf24SPI.transaction(operation) #Sends bytes in "operation" to nRF (first what register, than the bytes)
        return toReturn #Return bytes received from nRF
   
    def openPin(self):
        try:
            self.radio_pin.open() #Open the "CE" GPIO pin for access
            self.radio_pin.value=1 #Set the "CE" pin high (3,3V or 5V) to start listening for data
            time.sleep(LONG_PAUSE) #Listen 0,5s for incomming data
            self.radio_pin.value=0 #Ground the "CE" pin again, to stop listening
            self.radio_pin.close() #Close the CE-pin
        except(KeyboardInterrupt, SystemExit): #If ctrl+c breaks operation or system shutdown
            try:
                self.radio_pin.close() #First close the CE-pin, so that it can be opened again without error!
                print("\n\ngpio-pin closed!\n")
            except:
                pass
            raise #continue to break or shutdown!
		
    def init(self):
        #self.nrf24SPI = SPIDevice(0, 0) #Define SPI-unit (used in doOperation)
        self.nrf24SPI.speed_hz = 2000000#should set clock to 8MHz
        #self.openPin() self.radio_pin = pi_header_1.pin(22, direction=Out) #"CSN" on nRF, output self.radio_pin.open() self.radio_pin.value=0
        
        #1 Clear interrupts
        self.writeReg(STATUS,RH_NRF24_RX_DR | RH_NRF24_TX_DS | RH_NRF24_MAX_RT)
        
        #2 Enable dynamic payload length on all pipes
        self.writeReg(DYNPD,RH_NRF24_DPL_ALL)
        
        #3 Enable dynamic payload length, disable payload-with-ack, enable noack
        self.writeReg(FEATURE,RH_NRF24_EN_DPL | RH_NRF24_EN_DYN_ACK)
        
        #4 check if something is connected at all        
        tmp = self.readReg(FEATURE)#self.ReadPrintReg(FEATURE,"Feature",1) #
        #print (tmp)
        
        # test connection with radio device
        if int(tmp) != (RH_NRF24_EN_DPL | RH_NRF24_EN_DYN_ACK):
            print ("Init fail! Reason - no device!")
            self.radio_pin.close()
            return False
        
        #set network address self.changeAddress(0xE7)
        
        
        
        #5
        self.setModeIdle()
        
        #6
        self.flushTx()
        #7
        self.flushRx()
        #8
        self.setChannel(1)
        #9
        self.setRF(self.DataRate2Mbps,self.TransmitPower0dBm)
        
        return True
        
    def readReg(self,register):
        bytes = [READ_REG|register]
        bytes.append(COMMAND_NOP)
        ret = self.doOperation(duplex(bytes))
        Res = [hex(z)[2:] for z in ret[0]] #convert byte-array to string list
        #print (Res[1]) #debug
        return Res[1]
        
    def readRegister(self,register):
        bytes = [READ_REG|register]
        ret = self.doOperation(writing(bytes))
        return ret		
    
    #ACCENTURE
    def setPacket(self,nodeID,s1,s2,s3,s4):
        self._basicPacket = [COMMAND_W_TX_PAYLOAD_NOACK] #first addres TX register; this is not sent over radio
        self._basicPacket.extend([nodeID])	#sets node ID
        self._basicPacket.extend([s1])				#sets sensor 1 data
        self._basicPacket.extend([s2])				#sets sensor 1 data
        self._basicPacket.extend([s3])				#sets sensor 1 data
        self._basicPacket.extend([s4])				#sets sensor 1 data
    #end ACCENTURE
     
    def send2(self, data):
        if data.__len__() > NRF24_MAX_MESSAGE_LEN:
            return False
        
        _bytes = [COMMAND_W_TX_PAYLOAD_NOACK] 
        _bytes.extend([self._txHeaderTo])   		#this basically sets how packet looks
        _bytes.extend([self._txHeaderFrom])
        _bytes.extend([self._txHeaderId])
        _bytes.extend([self._txHeaderFlags])
        #bytes.append(data)
        data = [ord(str(x)) for x in data]
        _bytes.extend(data)
        
        self.setModeTx()
        #print(_bytes)
        #self.writeReg(COMMAND_W_TX_PAYLOAD_NOACK,_bytes)
        self.doOperation(writing(_bytes))
        return True
    
    def rcv(self):
        #print(self._bufLen)
        message = ""
        for x in range(0,self._bufLen): #.decode("utf-8")
             if x > 4:
                  #print(chr(self._buf[0][x]))
                  message += str(chr(self._buf[0][x]))
        #print("mess")
        #print(message)
        return message
        
    
    def waitPacketSent(self):
        if self._mode != self.RHModeTX:
            return False
        status = self.readReg(STATUS)
        #print("STATUS: ",end="")
        #print(int(status,16))
        while not(int(status,16) & (NRF24_TX_DS | NRF24_MAX_RT)):
            print ("TEST")#do nothing
        
        self.writeReg(STATUS,NRF24_TX_DS | NRF24_MASK_MAX_RT)
        if int(status,16) & NRF24_MASK_MAX_RT:
            self.flushTx()
        
        self.setModeIdle();
        
        return int(status,16) & NRF24_TX_DS
    
    def isSending(self):
        return not (self.writeReg(CONFIG,COMMAND_NOP) & NRF24_PRIM_RX) and not (self.writeReg(STATUS,COMMAND_NOP) & (NRF24_TX_DS|NRF24_MAX_RT))
        
    def validateRxBuf(self):
        #print(self._bufLen)
        if self._bufLen <4:
            return
        tmp = [hex(z)[2:] for z in self._buf[0]]
        #print(self._buf[0][1])
        
        self._rxHeaderTo = self._buf[0][1]
        self._rxHeaderFrom = self._buf[0][2]
        self._rxHeaderId = self._buf[0][3]
        self._rxHeaderFlags = self._buf[0][4]
        
        
        #print(self._thisAddress)
        #print(self._rxHeaderTo)
        #if self._promiscuous or self._rxHeaderTo == self._thisAddress or self._rxHeaderTo == self.B:
        if self._rxHeaderTo == self._thisAddress or self._rxHeaderTo == BROADCAST_ADDRESS:
            self._rxGood = int(self._rxGood + 1)
            #print(self._rxGood)
            self._rxBufValid = True
        #print(self._rxBufValid)
    
    def available(self):
        if not self._rxBufValid:
            #print("Starts")			
            if self._mode == self.RHModeTX:
                return False
            self.setModeRx()
            #9 - TO DO - check if this argument is true
            tmp = self.readReg(FIFO_STATUS)
            print("STAT: ",end="")            
            print(tmp)
            
            #print(int(tmp,16)) #debug
            if int(tmp,16) & NRF24_RX_EMPTY:
                #print ("Buffer empty")				
                return False
            tmp = self.readReg(COMMAND_R_RX_PL_WID) #0x60
            packLen = int(tmp) + 1
            #print ("LEN:")
            #print(tmp)
            len = int(tmp,16)
            #print("LEN: ")
            #print (len)
            if len>32:
                self.flushRx()
                self.clearRxBuf()
                self.setModeIdle()
                return False
            self.writeReg(STATUS,NRF24_RX_DR)	#0x27 => 0x40 clear IRQ

            self.burstRead(COMMAND_R_RX_PAYLOAD,self._buf,len)
            
            self._bufLen = len
            self.validateRxBuf()
            
            #print(self._rxBufValid)
            if self._rxBufValid:
                self.setModeIdle()
            #print(self._rxBufValid)
        return self._rxBufValid
    
    def burstRead(self,register,bufferData,length):        
        status = 0      
        #bufferData = self.ReadPrintReg(register,"RX Data", length)#reading(length)#doOperation(writing(register))
        bytes = [READ_REG|register] #First byte in "bytes" will tell the nRF what register to read from
        for x in range(0, length): #Add "numbers" amount of dummy-bytes to "bytes" to send to nRF
            bytes.append(COMMAND_NOP) #For each dummy byte sent to nRF later, a return byte will be collected
        self._buf = self.doOperation(duplex(bytes)) #Do the SPI operations (returns a byte-array with the bytes collected)        
        #print ("Received data:")
        #print (ret)
        return status
        
    def clearRxBuf(self):
        self._rxBufValid = False
        self._bufLen = 0
    
    def closeCEpin(self):
        self.radio_pin.close() #Close the CE-pin   
 
    def changeAddress(self,Addr):
        """Function to change address on both RX and TX"""
        bytes = [WRITE_REG|RX_ADDR_P0]
        bytes.extend([Addr,Addr,Addr,Addr,Addr])
        self.doOperation(writing(bytes))
 
        bytes = [WRITE_REG|TX_ADDR]
        bytes.extend([Addr,Addr,Addr,Addr,Addr])
        self.doOperation(writing(bytes))
    
    def clearRxTx(self):
        bytes=[WRITE_REG|STATUS]
        bytes.append(NRF24_TX_DS|NRF24_MAX_RT)
        self.doOperation(writing(bytes))
                        
if __name__ == "__main__":
    rxtx = input("rx or tx?\n")
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
                if (SendObj.available()): 
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
        
    
     
