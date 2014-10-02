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
LONG_PAUSE=0.5
 
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
        
        self._configuration = NRF24_EN_CRC | NRF24_CRCO
        self._chipEnablePin = 22
    
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
            _mode = self.RHModeIdle
    
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
            self.mode = self.RHModeTX
    
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
    
    def ReadPrintReg(self, Register, name, numbers):
        """Function that grabs "numbers" of bytes from the registry "Register" in the nRF and writes them out in terminal as "name....[0xAA,0xBB,0xCC]" """
        bytes = [READ_REG|Register] #First byte in "bytes" will tell the nRF what register to read from
        for x in range(0, numbers): #Add "numbers" amount of dummy-bytes to "bytes" to send to nRF
            bytes.append(COMMAND_NOP) #For each dummy byte sent to nRF later, a return byte will be collected
        ret = self.doOperation(duplex(bytes)) #Do the SPI operations (returns a byte-array with the bytes collected)
        #print(ret[0]) #debug print(hex(ord(ret[0]))) #debug print(bin(ord(ret[0]))) #debug
 
        Res = [hex(z)[2:] for z in ret[0]] #convert byte-array to string list
        #print(Res) #debug
 
        while len(name)<15: #Fill the name with "." so it allways becomes 15 char long (e.g. "STATUS.........")
            name = name + "."
 
        #Print out the register and bytes like this: "STATUS.........[0x0E]"
        print("{}".format(name), end='') #First print the name, and stay on same line (end='')
 
        for x in range(1, numbers+1): #Then print out every collected byte
            if len(Res[x]) == 1: #if byte started with "0" (ex. "0E") the "0" is gone from previous process => (len == 1)
                Res[x]= "0" + Res[x] #Readd the "0" if thats the case
            print("[0x{}]".format(Res[x].upper()), end='') #Print next byte after previous without new line
 
        print("") #Finnish with an empty print to contiune on new line and flush the print (no end='')
        return Res[1].upper() #Returns the first byte (not the zeroth which is allways STATUS)
    
 
    def receiveData(self):
        """Receive one or None messages from module"""
        #Reset Status registry
        bytes = [WRITE_REG|STATUS] #first byte to send tells nRF tat STATUS register is to be Written to
        bytes.append(RESET_STATUS) #add the byte that will be written to thr nRF (in this case the Reset command)
        self.doOperation(writing(bytes)) #execute the SPI command to send "bytes" to the nRF
 
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
 
        ret = self.doOperation(duplex([STATUS])) #Get the status register as byte-array
        
        Res = [hex(z)[2:] for z in ret[0]] #convert byte-array to string list
 
        Res = Res[0].upper() #Convert the interesting byte to one string, upper case (e.g. "4E")
        
        if len(Res) == 1: #if string started with "0" (ex. "0E") the "0" is gone from previous process => (len == 1)
            Res= "0" + Res #Readd the "0" if thats the case
            
        if(Res != "0E"): #If something is flagged in the STATUS-register
            self.ReadPrintReg(STATUS,"STATUS",1) #Print out the status-register
            if Res == "4E": #If data is received correctly
                self.ReadPrintReg(RD_RX_PLOAD,"Received",PAYLOAD_SIZE) #Print out the received bytes
        else:
            print(".", end='') #Print out dots to show we are still listening!
            sys.stdout.flush() #the end='' only puts it in the buffer!
 
    def send2(self, data):
        if data.__len__() > NRF24_MAX_MESSAGE_LEN:
            return False
        
        _bytes = [COMMAND_W_TX_PAYLOAD_NOACK]
        _bytes.extend([self._txHeaderTo])
        _bytes.extend([self._txHeaderFrom])
        _bytes.extend([self._txHeaderId])
        _bytes.extend([self._txHeaderFlags])
        #bytes.append(data)
        data = [ord(str(x)) for x in data]
        _bytes.extend(data)
        
        self.setModeTx()
        print(_bytes)
        #self.writeReg(COMMAND_W_TX_PAYLOAD_NOACK,_bytes)
        self.doOperation(writing(_bytes))
        return True
    
    def rcv2(self):
        if not (self.available()):
            return False
        
    
    def waitPacketSent(self):
        if self._mode != self.RHModeTX:
            return False
        status = self.readReg(STATUS)
        print("STATUS: ")
        print(status)
        while not(status & (NRF24_TX_DS | NRF24_MAX_RT)):
            print ("TEST")#do nothing
        
        self.writeReg(STATUS,NRF24_TX_DS | NRF24_MASK_MAX_RT)
        if _status & NRF24_MASK_MAX_RT:
            self.flushTx()
        
        self.setModeIdle();
        
        return _status & NRF24_TX_DS
    
    def isSending(self):
        return not (self.writeReg(CONFIG,COMMAND_NOP) & NRF24_PRIM_RX) and not (self.writeReg(STATUS,COMMAND_NOP) & (NRF24_TX_DS|NRF24_MAX_RT))
        
    def validateRxBuf(self):
        if self._bufLen <4:
            return
        self._rxHeaderTo = self._buf
        self._rxHeaderFrom = self._buf
        self._rxHeaderId = self._buf
        self._rxHeaderFlags = self._buf
        
        #if self._promiscuous or self._rxHeaderTo == self._thisAddress or self._rxHeaderTo == self.B:
        if self._rxHeaderTo == self._thisAddress or self._rxHeaderTo == BROADCAST_ADDRESS:
            self.rxGood = self.rxGood + 1
            self._rxBufValid = True
    
    def available(self):
        if not self._rxBufValid:
            if self._mode == self.RHModeTX:
                return False
            self.setModeRx()
            #9 - TO DO - check if this argument is true
            tmp = self.readReg(FIFO_STATUS)
            print("STAT: ")            
            print(tmp)
            
            #print(int(tmp,16)) #debug
            if int(tmp,16) & NRF24_RX_EMPTY:
                print ("Buffer empty")				
                return False
            tmp = self.readReg(COMMAND_R_RX_PL_WID) #0x60
            packLen = int(tmp) + 1
            print ("LEN:")
            print(tmp)
            len = int(tmp,16)
            #print("LEN: ")
            #print (len)
            if len>32:
                self.flushRx()
                self.clearRxBuf()
                self.setModeIdle()
                return False
            self.writeReg(STATUS,NRF24_RX_DR)	#0x27 => 0x40 clear IRQ
            #TO DO - BURST READ of data
            #self.writeReg(COMMAND_R_RX_PAYLOAD,self._buf)
            self.burstRead(COMMAND_R_RX_PAYLOAD,self._buf,14)
            
            self._bufLen = len
            self.validateRxBuf()
            
            if self._rxBufValid:
                self.setModeIdle()
        return self._rxBufValid
    
    def burstRead(self,register,bufferData,length):        
        status = 0
        bufferData = []
        #print("REGISTER: ")
        #print (writing(register))
        #self.writeReg(register,0)
        #self.doOperation(writing(register))
        self.nrf24SPI.send(register)# transaction(writing(register)) #should write 0x61 on MOSI
        #while(length):
        bufferData.append(self.nrf24SPI.recv(length))# transaction(writing(6)))
        #    length = length -1
        print ("Received data:")
        print (bufferData)
        return status
        
    def clearRxBuf(self):
        self._rxBufValid = False
        self._bufLen = 0
    
    def closeCEpin(self):
        self.radio_pin.close() #Close the CE-pin
    
    def sendData(self,toSend):
        """Sends x bytes of data"""
        #Reset Status registry for next transmission
        bytes = [WRITE_REG|STATUS] #first byte to send tells nRF tat STATUS register is to be Written to
        bytes.append(RESET_STATUS) #add the byte that will be written to thr nRF (in this case the Reset command)
        self.doOperation(writing(bytes)) #execute the SPI command to send "bytes" to the nRF
 
        #Flush RX Buffer
        self.doOperation(writing([FLUSH_TX])) #This one is special because it doesn't need any more than one byte SPI-command.
                                                #This is because the FLUSH_TX is located on the top level on the nRF, same as the "WRITE_REG" register or the 
                                                #"READ_REG". (See datasheet Tabel 8)
        
        #Print out the STATUS registry before transmission
        self.ReadPrintReg(STATUS,"STATUS before",1)
 
        #Print out the transmitting bytes with quotations ("chr(34)"), Payload cannot be read from the nRF!
        print("Transmitting...[{}{}{},{}{}{},{}{}{}]".format(chr(34), chr(toSend[0]),chr(34),chr(34), chr(toSend[1]), chr(34), chr(34),chr(toSend[2]),chr(34)))
 
        #This checks if the payload is"900" or "901", 002, 003 or 004, and if so, changes the address on the nRF.
        a = "".join([chr(x) for x in toSend])
        #print(a)
        if(a=="900" or a=="901"):
            self.changeAddress(0x13) #Calls function located further down
        elif(a=="002" or a=="003" or a=="004"):#
              self.changeAddress(0x14)
 
        #Print out the address one more time, to make sure it is sent to the right receiver.
        self.ReadPrintReg(RX_ADDR_P0,"To",5)
        
        #write bytes to send into tx buffer
        bytes = [WR_TX_PLOAD] #This one is simular to FLUSH_TX because it is located on the same top level in the nRF,
                                #Even though we want to write to it, we cannot add the "WERITE_REG" command to it!
        bytes.extend(toSend) #Because we now want to add a byte array to it, we use the "extend(" command instead of "append("
        self.doOperation(writing(bytes)) #Write payload to nRF with SPI
        print(bytes)
        try:
            self.radio_pin.open() #Open the "CE" GPIO pin for access
            self.radio_pin.value=1 #Set the "CE" pin high (3,3V or 5V) to start transmission
            time.sleep(0.001) #Send for 0,5s to make sure it has time to send it all
            self.radio_pin.value=0 #Ground the CE pin again, to stop transmission
            self.radio_pin.close() #Close the CE-pin
            
        except(KeyboardInterrupt, SystemExit): #If ctrl+c breaks operation or system shutdown
            try:
                self.radio_pin.close() #First close the CE-pin, so that it can be opened again without error!
                print("\n\ngpio-pin closed!\n")
            except:
                pass
            raise #continue to break or shutdown!
        
        self.ReadPrintReg(STATUS,"STATUS after",1) #Read STATUS register that hopefully tells you a successful transmission has occured (0x2E)
        print("")
        
        if(a=="900" or a=="901" or a=="002" or a=="003" or a=="004"): #If you changed address above, change it back to normal
            self.changeAddress(0x12) #Change back address!
 
 
    def changeAddress(self,Addr):
        """Function to change address on both RX and TX"""
        bytes = [WRITE_REG|RX_ADDR_P0]
        bytes.extend([Addr,Addr,Addr,Addr,Addr])
        self.doOperation(writing(bytes))
 
        bytes = [WRITE_REG|TX_ADDR]
        bytes.extend([Addr,Addr,Addr,Addr,Addr])
        self.doOperation(writing(bytes))
        
    def setupRadio(self):
        """Function that sets the basic settings in the nRF"""
        #Setup EN_AA
        bytes = [WRITE_REG|EN_AA]
        bytes.append(SET_ACK)
        self.doOperation(writing(bytes))
 
        #Setup ACK RETRIES
        bytes = [WRITE_REG|SETUP_RETR]
        bytes.append(SET_ACK_RETR)
        self.doOperation(writing(bytes))
 
        #Setup Datapipe
        bytes = [WRITE_REG|EN_RXADDR]
        bytes.append(SET_DATAPIPE)
        self.doOperation(writing(bytes))
 
        #Setup Address width
        bytes = [WRITE_REG|SETUP_AW]
        bytes.append(SET_ADR_WIDTH)
        self.doOperation(writing(bytes))
 
        #freq //channel
 
        #Setup Data speed and power
        bytes = [WRITE_REG|RF_SETUP]
        bytes.append(SET_SETUP)
        self.doOperation(writing(bytes))
 
        #Setup Receive Address
        bytes = [WRITE_REG|RX_ADDR_P0]
        bytes.extend(SET_RX_ADDR_P0) #"extend" adds a list to a list, "append" adds one obect to a list
        self.doOperation(writing(bytes))
 
        #Setup Transmitter Address
        bytes = [WRITE_REG|TX_ADDR]
        bytes.extend(SET_TX_ADDR)
        self.doOperation(writing(bytes))
 
        #Setup Payload size
        bytes = [WRITE_REG|RX_PW_P0]
        bytes.append(SET_PAYLOAD_S)
        self.doOperation(writing(bytes))
                
        #Setup CONFIG registry
        bytes = [WRITE_REG|CONFIG]
        bytes.append(SET_CONFIG)
        self.doOperation(writing(bytes))
        time.sleep(LONG_PAUSE)
 
        #Collect print out the registers from the nRF to to make sure thay are allright
        self.ReadPrintReg(STATUS,"STATUS",1)
        self.ReadPrintReg(EN_AA,"EN_AA",1)
        self.ReadPrintReg(SETUP_RETR,"SETUP_RETR",1)
        self.ReadPrintReg(EN_RXADDR,"EN_RXADDR",1)
        self.ReadPrintReg(SETUP_AW,"SETUP_AW",1)
        self.ReadPrintReg(RF_CH,"RF_CH",1)
        self.ReadPrintReg(RF_SETUP,"RF_SETUP",1)
        self.ReadPrintReg(RX_ADDR_P0,"RX_ADDR_P0",5)
        self.ReadPrintReg(TX_ADDR,"TX_ADDR",5)
        self.ReadPrintReg(RX_PW_P0,"RX_PW_P0",1)
        self.ReadPrintReg(CONFIG,"CONFIG",1)
 
        #self.radio_pin.close()
                
def Send(data):
    """Function that can be called from other files that wants to send data"""
    SendObj = RH_NRF24()
    SendObj.sendData(data)
    print("Enter data to send (3 bytes): ") #Retype the input-text (input is still on form main-loop)
 
if __name__ == "__main__":
    rxtx = input("rx or tx?")
    SendObj = RH_NRF24() #Start class
    try:
        if rxtx == 'tx':
            print("Transmiter..\n")
            SendObj.init() #OK
            #SendObj.setModeTx
            #av = SendObj.available() SendObj.sendData("hello world")
            SendObj.send2("Hello world ;)")
            print(SendObj.readReg(FIFO_STATUS))
            SendObj.setModeTx()
            if not(SendObj.waitPacketSent()):
                print("Send SUCCESS")
            SendObj.radio_pin.value = 0
            SendObj.closeCEpin()
        elif rxtx == 'rx':
            print("Receive..\n")
            SendObj.init()
            SendObj.send2("Hello world ;)")
            print(SendObj.readReg(FIFO_STATUS)) #0x17
            SendObj.setModeTx()
            if not(SendObj.waitPacketSent()):
                print("Send SUCCESS")
            SendObj.setModeRx()
            notReceived = 0
            
            while(not notReceived):
                if SendObj.available():
                     print("Available")
                else:
                     time.sleep(0.005)
                     print(".")
            SendObj.radio_pin.value = 0
            SendObj.closeCEpin()
            
    except(KeyboardInterrupt, SystemExit): #If ctrl+c breaks operation or system shutdown
            try:
                self.radio_pin.close() #First close the CE-pin, so that it can be opened again without error!
                print("\n\ngpio-pin closed!\n")
            except:
                pass
            raise #continue to break or shutdown!
     
