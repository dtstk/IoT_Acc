#Project based on Radio Head NRF24 library - http://www.airspayce.com/mikem/arduino/RadioHead/
#and Kalle Lofgren - http://gizmosnack.blogspot.com/2013_05_01_archive.html
#Implemented by Gundars Miezitis, 07.10.2014

#necesary libraries
from quick2wire.spi import * 
from quick2wire.gpio import Pin
from quick2wire.gpio import In,Out,pi_header_1,Rising
import time 
from random import randint

#Definitions of registers
#Define Packet size 
NRF24_MAX_PAYLOAD_LEN = 32 
NRF24_HEADER_LEN = 4
NRF24_HEADER_LEN_ACC = 1 # for ACC project purposes
NRF24_MAX_MESSAGE_LEN = NRF24_MAX_PAYLOAD_LEN - NRF24_HEADER_LEN 
NRF24_MAX_MESSAGE_LEN_ACC = NRF24_MAX_PAYLOAD_LEN - NRF24_HEADER_LEN_ACC # for ACC project purposes

#define necesary NRF24 chip values used in setting up radi chip
TransmitPowerm18dBm = 0
TransmitPowerm12dBm = 1
TransmitPowerm6dBm = 2
TransmitPower0dBm = 3
DataRate1Mbps = 0
DataRate2Mbps = 1
DataRate250kbps = 2
AddressWidth3bytes = 1
AddressWidth4bytes = 2
AddressWidth5bytes = 3
ModeIdle = 0
ModeRX = 1
ModeTX = 2
BROADCAST_ADDRESS = 0xff

#define NRF24_REG_00_CONFIG 0x00
NRF24_MASK_RX_DR = 0x40 
NRF24_MASK_TX_DS = 0x20 
NRF24_MASK_MAX_RT = 0x10 
NRF24_EN_CRC = 0x08 
NRF24_CRCO = 0x04 
NRF24_PWR_UP = 0x02 
NRF24_PRIM_RX = 0x01

#define NRF24_REG_01_EN_AA 0x01
NRF24_ENAA_ALL = 0x3F
NRF24_ENAA_P5 = 0x20 
NRF24_ENAA_P4 = 0x10 
NRF24_ENAA_P3 = 0x08 
NRF24_ENAA_P2 = 0x04  
NRF24_ENAA_P1 = 0x02
NRF24_ENAA_P0 = 0x01

#define NRF24_REG_02_EN_RXADDR 0x02
NRF24_ERX_P5 = 0x20 
NRF24_ERX_P4 = 0x10 
NRF24_ERX_P3 = 0x08 
NRF24_ERX_P2 = 0x04 
NRF24_ERX_P1 = 0x02
NRF24_ERX_P0 = 0x01

#define NRF24_REG_03_SETUP_AW 0x03
NRF24_AW_3_BYTES = 0x01 
NRF24_AW_4_BYTES = 0x02
NRF24_AW_5_BYTES = 0x03

#define NRF24_REG_04_SETUP_RETR 0x04
NRF24_ARD = 0xf0
NRF24_ARC = 0x0f

#define NRF24_REG_05_RF_CH 0x05
NRF24_RF_CH = 0x7F

#define NRF24_REG_06_RF_SETUP 0x06
NRF24_CONT_WAVE = 0x80 
NRF24_RF_DR_LOW = 0x20 
NRF24_PLL_LOCK = 0x10 
NRF24_RF_DR_HIGH = 0x08 
NRF24_PWR = 0x06 
NRF24_PWR_m18dBm = 0x00 
NRF24_PWR_m12dBm = 0x02 
NRF24_PWR_m6dBm = 0x04 
NRF24_PWR_0dBm = 0x06

#define NRF24_REG_07_STATUS 0x07
NRF24_RX_DR = 0x40 
NRF24_TX_DS = 0x20 
NRF24_MAX_RT = 0x10 
NRF24_RX_P_NO = 0x0e 
NRF24_STATUS_TX_FULL = 0x01

#define NRF24_REG_08_OBSERVE_TX 0x08
NRF24_PLOS_CNT = 0xf0
NRF24_ARC_CNT  = 0x0f

#define NRF24_REG_09_RPD 0x09
NRF24_RPD = 0x01

#define NRF24_REG_17_FIFO_STATUS 0x17
NRF24_TX_REUSE = 0x40 
NRF24_TX_FULL = 0x20 
NRF24_TX_EMPTY = 0x10 
NRF24_RX_FULL = 0x02 
NRF24_RX_EMPTY = 0x01

#define NRF24_REG_1C_DYNPD 0x1c
NRF24_DPL_ALL = 0x3f 
NRF24_DPL_P5 = 0x20 
NRF24_DPL_P4 = 0x10 
NRF24_DPL_P3 = 0x08 
NRF24_DPL_P2 = 0x04 
NRF24_DPL_P1 = 0x02 
NRF24_DPL_P0 = 0x01

#define NRF24_REG_1D_FEATURE 0x1d
NRF24_EN_DPL = 0x04 
NRF24_EN_ACK_PAY = 0x02 
NRF24_EN_DYN_ACK = 0x01

#NRF24 register ADDRESSES:
NRF24_REG_00_CONFIG 		= 0x00 
NRF24_REG_01_EN_AA 			= 0x01 
NRF24_REG_02_EN_RXADDR 		= 0x02 
NRF24_REG_03_SETUP_AW 		= 0x03 
NRF24_REG_04_SETUP_RETR 	= 0x04 
NRF24_REG_05_RF_CH 			= 0x05 
NRF24_REG_06_RF_SETUP 		= 0x06 
NRF24_REG_07_STATUS 		= 0x07 
NRF24_REG_08_OBSERVE_TX 	= 0x08 
NRF24_REG_09_CD 			= 0x09 #RPD
NRF24_REG_0A_RX_ADDR_P0 	= 0x0A 
NRF24_REG_0B_RX_ADDR_P1 	= 0x0B 
NRF24_REG_0C_RX_ADDR_P2 	= 0x0C 
NRF24_REG_0D_RX_ADDR_P3 	= 0x0D 
NRF24_REG_0E_RX_ADDR_P4 	= 0x0E 
NRF24_REG_0F_RX_ADDR_P5 	= 0x0F 
NRF24_REG_10_TX_ADDR 		= 0x10 
NRF24_REG_11_RX_PW_P0 		= 0x11 
NRF24_REG_12_RX_PW_P1 		= 0x12 
NRF24_REG_13_RX_PW_P2 		= 0x13 
NRF24_REG_14_RX_PW_P3 		= 0x14 
NRF24_REG_15_RX_PW_P4 		= 0x15 
NRF24_REG_16_RX_PW_P5 		= 0x16 
NRF24_REG_17_FIFO_STATUS 	= 0x17 
NRF24_REG_1C_DYNPD 			= 0x1C 
NRF24_REG_1D_FEATURE 		= 0x1D
 
#SPI Command names
COMMAND_R_REGISTER = 0x00 
COMMAND_W_REGISTER = 0x20 
COMMAND_ACTIVATE = 0x50 
COMMAND_R_RX_PAYLOAD = 0x61 
COMMAND_W_TX_PAYLOAD = 0xa0 
COMMAND_FLUSH_TX = 0xe1 
COMMAND_FLUSH_RX = 0xe2 
COMMAND_REUSE_TX_PL = 0xe3 
COMMAND_R_RX_PL_WID = 0x60 
COMMAND_W_TX_PAYLOAD_NOACK = 0xb0 
COMMAND_NOP = 0xff 

def COMMAND_W_ACK_PAYLOAD(self,pipe): 
    return (0xa8|(pipe&0x7))     


class NRF24:
    ''' Class implementing all communication with NRF24L01P'''
    def __init__(self):
        """__init__ function is allways run first, when the class is called!"""
        """Here we define ALL necesary class variables for operation"""
        self._nrf24SPI = SPIDevice(0, 0) #Define SPI-unit (used in doOperation)
        self._radio_pin = pi_header_1.pin(22, direction=Out) #"CE" on nRF, output
        #self._radio_pin.open() #openin pin so that it's state could be changed

        try:
            self._radio_pin.open() #openin pin so that it's state could be changed
        except:
            print("Do nothing!")
            #self._radio_pin.close() #openin pin so that it's state could be changed
            #self._radio_pin.open() #openin pin so that it's state could be changed

        self._mode = -1 #defines default mode which is not operational
        self._rxBufValid = 0
        self._buf = ""
        #not for all packets..
        self._txHeaderTo = 0xFF
        self._txHeaderFrom = 0xFF
        self._txHeaderId = 0x00
        self._txHeaderFlags = 0x00
        #comm with MIRF
        self._thisAddress = 0xff #default address
        self._rxGood=0
        
        self._configuration = NRF24_EN_CRC #| NRF24_CRCO #default configuration
        self._chipEnablePin = 22
        
        self._packetHeaderLength = 1
        #related to ACCENTURE application
        self._basicPacket = []
        #self._nodeID = 44
        
        #defiene necesary for init
        self._packetLength = 5 #used to define PIPE length
        self._enAutoACK = True #enable on ALL pipes
        self._addresWidth = AddressWidth5bytes #5byte address
        self._autoRetransmitDelay = 250
        self._autoRetransmitCount = 3
        self._channel = 100
        self._transferRate = DataRate2Mbps
        self._transferPower = TransmitPower0dBm
        self._continiouseWave = False
        self._SPISpeed = 1000000
        self._pipeLength = 5
        self._carrierDetect = False #BUG
        
    '''Object functions to set up NRF24'''
    # register CONFIG 0x00
    def setConfiguration(self):
        self._configuration = NRF24_EN_CRC #| NRF24_CRCO
        
    def setModeIdle(self):
        """Switches NRF24 to IDLE mode, no TX, no RX"""
        if (self._mode != ModeIdle):
            self.writeReg(NRF24_REG_00_CONFIG,self._configuration)
            self._radio_pin.value = 0
            self._mode = ModeIdle
    
    def setModeRx(self):
        """Switches NRF24 to RECEVE mode"""
        if self._mode != ModeRX:
            self.writeReg(NRF24_REG_00_CONFIG,self._configuration | NRF24_PWR_UP | NRF24_PRIM_RX)
        self._radio_pin.value=1
        self._mode = ModeRX
        
    def setModeTx(self):
        """Switches NRF24 to TRANSMIT mode"""
        if self._mode != ModeTX:
            self._radio_pin.value = 0
            self.writeReg(NRF24_REG_00_CONFIG,self._configuration | NRF24_PWR_UP)
            self._radio_pin.value = 1
            self._mode = ModeTX
            
    # register EN_AA 0x01
    def setAutoACK(self,pipe):
        """Enables auto ACK on specified pipe"""
        tmp = self.readReg(NRF24_REG_01_EN_AA)
        self.writeReg(NRF24_REG_01_EN_AA, int(tmp,16) | 1 << pipe)
    
    def clearAutoACK(self,pipe):
        """Clears AutoACK on specified pipe"""
        tmp = self.readReg(NRF24_REG_01_EN_AA)
        self.writeReg(NRF24_REG_01_EN_AA, int(tmp,16) & ~(1 << pipe))
    
    def setAutoACKAll(self):
        self.writeReg(NRF24_REG_01_EN_AA, NRF24_ENAA_ALL)

    def clearAutoACKAll(self):
        for x in range(0,6):
            self.clearAutoACK(x)

    # register EN_RXADDRE 0x02
    def enableRXPipe(self,pipe):
        """Sets RX pipe on"""
        tmp = self.readReg(NRF24_REG_02_EN_RXADDR)
        self.writeReg(NRF24_REG_02_EN_RXADDR, int(tmp,16) | (1 << pipe))

    def disableRXPipe(self,pipe):            
        """Turn of specified pipe on RX"""
        tmp = self.readReg(NRF24_REG_02_EN_RXADDR)
        self.writeReg(NRF24_REG_02_EN_RXADDR, int(tmp,16) & ~(1 << pipe))
    
    #register SETUP_AW 0x03
    def setUpAdressWidth(self,width):
        self.writeReg(NRF24_REG_03_SETUP_AW,width)

    #register SETUP_RETR 0x04
    def setAutoRetransmit(self,count,delay):
        """250 - 0000 us to 4000 - 1111 us"""	
        if delay>4000 or delay<250:
            print ("Delay must be between 250 - 4000 uS")
            return 0
        delay = (int(delay / 250)-1) << 4
        
        #tmp = int(self.readReg(NRF24_REG_04_SETUP_RETR),16)
        tmp = (delay & 0xf0) | (count & 0x0f)
        self.writeReg(NRF24_REG_04_SETUP_RETR, tmp)       

    #register RF_CH 0x05
    def setChannel(self,channel):
        """Sets up RF_CH - 0x05 register"""
        self.writeReg(NRF24_REG_05_RF_CH,channel & NRF24_RF_CH)
        return True
        
    #register RF_SETUP 0x06
    def setRF(self,data_rate,power):
        """Sets up RF_SETUP - 0x06 register"""
        _value = (power << 1) & NRF24_PWR #if DR = 1Mbps
        #print (data_rate)
        if data_rate == DataRate250kbps:
            _value |= NRF24_RF_DR_LOW
        #    print("Set 250kbps")
        elif data_rate == DataRate2Mbps:
            _value |= NRF24_RF_DR_HIGH
        #    print("Set 2Mbps") else: print("Set 1Mbps") print (_value)
        self.writeReg(NRF24_REG_06_RF_SETUP,_value)
        return True

    def setContiniouseWave(self):
        tmp = int(self.readReg(NRF24_REG_06_RF_SETUP),16)
        tmp = tmp & 0x7F | NRF24_CONT_WAVE
        self.writeReg(NRF24_REG_06_RF_SETUP,tmp)
    
    def clearContiniouseWawe(self):
        tmp = int(self.readReg(NRF24_REG_06_RF_SETUP),16)
        tmp = tmp & 0x7F & ~NRF24_CONT_WAVE
        self.writeReg(NRF24_REG_06_RF_SETUP,tmp)
    
    # register STATUS 0x07
    def clearInterupts(self):
        self.writeReg(NRF24_REG_07_STATUS,NRF24_RX_DR | NRF24_TX_DS | NRF24_MAX_RT)       
    
    #register CD 0x09
    def setCD(self):
        self.writeReg(NRF24_REG_09_CD,NRF24_RPD)
        #tmp = self.readReg(NRF24_REG_09_CD)
    
    def clearCD(self):
        self.writeReg(NRF24_REG_09_CD,0)
        #tmp = self.readReg(NRF24_REG_09_CD)
        
    #register RX_ADDR_Px 0x0A - 0x0F
    def setRXAddress(self,pipeNr,address):
        """Set RX address on specified pipe"""
        bytes = [COMMAND_W_REGISTER|(NRF24_REG_0A_RX_ADDR_P0+pipeNr)]
        tmp = []
        for x in address:
            tmp.append(ord(x))
        bytes.extend(tmp)
        bytes.append(0)
        #print(bytes)
        ret = self.doOperation(writing(bytes))
    
    #register TX_ADDR 0x10
    def setTXAddress(self,address):
        """Set TX address of this node"""
        bytes = [COMMAND_W_REGISTER|NRF24_REG_10_TX_ADDR]
        tmp = []
        for x in address:
            tmp.append(ord(x))
        bytes.extend(tmp)
        bytes.append(0)
        #print(bytes)
        ret = self.doOperation(writing(bytes))
    
    #register RX_PW_Px 0x11 - 0x16
    def setPipeLength(self,pipe,length):
        """Sets allowed RX data length on specified PIPE"""
        bytes=[COMMAND_W_REGISTER|(NRF24_REG_11_RX_PW_P0+pipe)]
        bytes.append(length)
        ret = self.doOperation(writing(bytes))  
        
    #register FIFO_STATUS 0x17
    def getFIFOStatus(self):
        return self.readReg(NRF24_REG_17_FIFO_STATUS)
        
        
    #other    
    
    def flushTx(self):
        """Empties TX buffer"""
        self.writeTopReg(COMMAND_FLUSH_TX)
    
    def flushRx(self):
        """Empties RX buffer"""
        self.writeTopReg(COMMAND_FLUSH_RX)

    '''Low level interface between RPi and NRF24'''
    def writeReg(self,register,value):
        """Writes specified register with suplied value"""
        bytes = [COMMAND_W_REGISTER|register]
        bytes.append(value)
        return self.doOperation(writing(bytes))

    def writeTopReg(self,register):
        """Writes top level Register. Used to Flush RX and TX"""		
        bytes = [register]
        return self.doOperation(writing(bytes))
    
    def readReg(self,register):
        """Reads specified register and returns it value"""		
        bytes = [COMMAND_R_REGISTER|register]
        bytes.append(COMMAND_NOP)
        ret = self.doOperation(duplex(bytes))
        Res = [hex(z)[2:] for z in ret[0]] #convert byte-array to string list
        #print (Res[1]) #debug
        return Res[1]        
            
    def doOperation(self,operation):
        """Do one SPI operation"""
        toReturn = self._nrf24SPI.transaction(operation) #Sends bytes in "operation" to nRF (first what register, than the bytes)
        return toReturn #Return bytes received from nRF

    def burstRead(self,register,bufferData,length): 
        """Reads specified lenght data from register"""       
        status = 0      
        bytes = [COMMAND_R_REGISTER|register] #First byte in "bytes" will tell the nRF what register to read from
        for x in range(0, length): #Add "numbers" amount of dummy-bytes to "bytes" to send to nRF
            bytes.append(COMMAND_NOP) #For each dummy byte sent to nRF later, a return byte will be collected
        self._buf = self.doOperation(duplex(bytes)) #Do the SPI operations (returns a byte-array with the bytes collected)        
        return status 

    def printRegisterMap(self):
        #Print register map
        for x in range(0,17):
            print ("Register ", x, " :", end="")
            print(int(self.readReg(x),16))      

    '''Functions responsible for setting up NRF24'''
    def init(self):
        """Basic init function"""		
        self._nrf24SPI.speed_hz = 2000000# set clock to 2MHz
        #1 Clear interrupts
        self.clearInterupts()
        #2 Enable dynamic payload length on all pipes
        self.writeReg(NRF24_REG_1C_DYNPD,NRF24_DPL_ALL)       
        #3 Enable dynamic payload length, disable payload-with-ack, enable noack
        self.writeReg(NRF24_REG_1D_FEATURE,NRF24_EN_DPL | NRF24_EN_DYN_ACK)        
        #4 check if something is connected at all        
        tmp = self.readReg(NRF24_REG_1D_FEATURE)#self.ReadPrintReg(FEATURE,"Feature",1) #       
        # test connection with radio device
        if int(tmp,16) != (NRF24_EN_DPL | NRF24_EN_DYN_ACK):
            print ("Init fail! Reason - no device!")
            self._radio_pin.close()
            return False
        #5 
        self.setModeIdle()       
        #6
        self.flushTx()
        #7
        self.flushRx()
        #8
        self.setChannel(1)
        #9
        self.setRF(DataRate2Mbps,TransmitPower0dBm)        
        return True

    def initNRF24(self):
        """One by one initializes relevant register of NRF24"""        
        #SPI
        self._nrf24SPI.speed_hz = self._SPISpeed
        
        #NRF24
        self.setModeIdle() #CONFIG
        if self._enAutoACK:
            self.setAutoACKAll() #EN_AA
        
        self.setPipeLength(0,self._packetLength)
        self.setPipeLength(1,self._packetLength)
        
        self.setUpAdressWidth(self._addresWidth)
        self.setAutoRetransmit(self._autoRetransmitCount,self._autoRetransmitDelay)
            
        self.setChannel(self._channel)
        self.setRF(self._transferRate,self._transferPower)
        self.clearInterupts()
        self.flushRx()
        self.flushTx()
        return True
        
    def initForMirf(self):
        """Initializes for communication with MIRF Arduino for master node"""
        self._nrf24SPI.speed_hz = 1000000
        self.setRXAddress(1,'serv')
        self.setRXAddress(0,'cln1')
        self.setTXAddress('cln1')
        self.setChannel(100)
        self.setPipeLength(0,5)
        self.setPipeLength(1,5)
        self.setModeRx()      
        self.writeReg(NRF24_REG_07_STATUS, NRF24_TX_DS | NRF24_MAX_RT) 
        self.writeReg(NRF24_REG_01_EN_AA, 63) # disable or enable ACK
        self.flushTx()
        self.flushRx()
        self.setRF(DataRate2Mbps,TransmitPower0dBm)        
        return True   
        
    '''Functions that enable reception and transmission of data packets'''	
    def sendMIRF(self):
        self.setModeTx()
        #print("Data replay: ", end="")
        #print(self._basicPacket)
        #self.writeReg(COMMAND_W_TX_PAYLOAD_NOACK,_bytes)
        self.doOperation(writing(self._basicPacket))
        return True
     
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
    
    def rcvAllPacket(self):
        """Reads ALL receved message from buffer"""
        #print(self._bufLen)
        message = []
        for x in range(0,self._bufLen): #.decode("utf-8")
             if x > 0:                  
                  #print((self._buf[0][x]))
                  message.append((self._buf[0][x]))
        return message
        
    def rcvWithoutHeader(self):
        """Reads receveid packet without header"""
        message = []
        for x in range(0,self._bufLen): #.decode("utf-8")
             if x > self._packetHeaderLength:                  
                  message.append((self._buf[0][x]))
                  #message += str(chr(self._buf[0][x])) #if data is string
        return message
        
    def rcvString(self):
        """Reads received data without header and transforms it to string"""        
        message = ""
        for x in range(0,self._bufLen): #.decode("utf-8")
             if x > self._packetHeaderLength:                                    
                  message += str(chr(self._buf[0][x])) #if data is string
        return message
        
    def waitPacketSent(self):
        """Blocks NRF24 further operation until packet is sent"""
        if self._mode != ModeTX:
            return False
        status = self.readReg(NRF24_REG_07_STATUS)
        while not(int(status,16) & (NRF24_TX_DS | NRF24_MAX_RT)):
            pass #do nothing
        
        self.writeReg(NRF24_REG_07_STATUS,NRF24_TX_DS | NRF24_MASK_MAX_RT)
        if int(status,16) & NRF24_MASK_MAX_RT:
            self.flushTx()
        
        self.setModeIdle();
        #print(int(status,16) & NRF24_TX_DS)
        return int(status,16) & NRF24_TX_DS
    
    def isSending(self):
        """Tests if packet is still sending or not"""
        return not (self.writeReg(NRF24_REG_00_CONFIG,COMMAND_NOP) & NRF24_PRIM_RX) and not (self.writeReg(NRF24_REG_07_STATUS,COMMAND_NOP) & (NRF24_TX_DS|NRF24_MAX_RT))
            
    def available(self,readRegister):
        """Checks FIFO_STATUS if data is received or not. If received reads data into buffer"""
        if not self._rxBufValid:			
            if self._mode == ModeTX:
                return False
            tmp = self.getFIFOStatus()
            #tmp1 = self.readReg(NRF24_REG_07_STATUS)
            #print(tmp1)
            if int(tmp,16) & NRF24_RX_EMPTY:
                #print ("Buffer empty")				
                return False
            tmp = self.readReg(COMMAND_R_RX_PL_WID) #0x60
            
            packLen = int(tmp) + 1
            
            if packLen>32: #if received more than allowed buffer
                self.flushRx()
                self.clearRxBuf()
                self.setModeIdle()
                return False
            self.writeReg(NRF24_REG_07_STATUS,NRF24_RX_DR)	#0x27 => 0x40 clear IRQ

            self.burstRead(readRegister,self._buf,packLen) #reads received packet and writes it in buffer
            
            self._bufLen = packLen
            self.validateRxBuf()

            if self._rxBufValid:
                self.setModeIdle()
            #print(self._rxBufValid)
        return self._rxBufValid
    
                   
    def closeCEpin(self):
        """Closes CE pin"""
        self._radio_pin.close() #Close the CE-pin   

    '''Functions related to packet'''    
    #ACCENTURE
    def setPacket(self,nodeID,s1,s2,s3,s4):
        """Sets default packet values""" 
        self._basicPacket = [COMMAND_W_TX_PAYLOAD_NOACK] 		
        self._basicPacket.extend([nodeID])			#sets node ID
        self._basicPacket.extend([s1])				#sets sensor 1 data
        self._basicPacket.extend([s2])				#sets sensor 2 data
        self._basicPacket.extend([s3])				#sets sensor 3 data
        self._basicPacket.extend([s4])				#sets sensor 4 data
    #end ACCENTURE    
    
    def validateRxBuf(self):
        """Checks if received packet was ment for this node and if it id the correct format"""
        #print(self._bufLen)
        if self._bufLen <4:
            return
        tmp = [hex(z)[2:] for z in self._buf[0]]
        #print(self._buf[0][1])
        
        self._rxHeaderTo = self._buf[0][1]
        self._rxHeaderFrom = self._buf[0][2]
        self._rxHeaderId = self._buf[0][3]
        self._rxHeaderFlags = self._buf[0][4]
        
        
        #print(self._thisAddress) #255
        #print(self._rxHeaderTo)  #1
        #if self._promiscuous or self._rxHeaderTo == self._thisAddress or self._rxHeaderTo == self.B:
        if self._rxHeaderTo == self._thisAddress or self._rxHeaderTo == BROADCAST_ADDRESS:
            self._rxGood = int(self._rxGood + 1)
            #print(self._rxGood)
            self._rxBufValid = True
        #print(self._rxBufValid)    

    def clearRxBuf(self):
        """Sets variables to notifie that RX is done"""
        self._rxBufValid = False
        self._bufLen = 0

