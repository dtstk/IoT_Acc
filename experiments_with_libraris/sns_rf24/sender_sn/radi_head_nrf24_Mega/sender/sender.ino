// nrf24_client.pde
// -*- mode: C++ -*-
// Example sketch showing how to create a simple messageing client
// with the RH_NRF24 class. RH_NRF24 class does not provide for addressing or
// reliability, so you should only use RH_NRF24 if you do not need the higher
// level messaging abilities.
// It is designed to work with the other example nrf24_server.
// Tested on Uno with Sparkfun NRF25L01 module
// Tested on Anarduino Mini (http://www.anarduino.com/mini/) with RFM73 module
// Tested on Arduino Mega with Sparkfun WRL-00691 NRF25L01 module

#include <SPI.h>
#include <RH_NRF24.h>

// Singleton instance of the radio driver
//RH_NRF24 nrf24;
// RH_NRF24 nrf24(8, 7); // use this to be electrically compatible with Mirf
RH_NRF24 nrf24(48, 49);// For Leonardo, need explicit SS pin (CE,CSN)
// RH_NRF24 nrf24(8, 7); // For RFM73 on Anarduino Mini
void printSettings()
{
  int i=0;
  for (i=0; i<=23;i++)
  Serial.println(nrf24.spiReadRegister(i));
}

uint8_t* address = (uint8_t*)231;

void setup() 
{
  Serial.begin(9600);
  while (!Serial) 
    ; // wait for serial port to connect. Needed for Leonardo only
  Serial.println("start");
  if (!nrf24.init())
    Serial.println("init failed");
  else
    Serial.println("init success");
  // Defaults after init are 2.402 GHz (channel 2), 2Mbps, 0dBm
  if (!nrf24.setChannel(1))
    Serial.println("setChannel failed");
  else
    Serial.println("setChannel success");
  if (!nrf24.setRF(RH_NRF24::DataRate1Mbps, RH_NRF24::TransmitPower0dBm))
    Serial.println("setRF failed");    
  else
    Serial.println("setRF success");
    
    if(!nrf24.setNetworkAddress(address,5))
      Serial.println("setaddress failed" );
    else
      Serial.println("setaddress success" );
}


void loop()
{
  Serial.print(".");
  // Send a message to nrf24_server
  uint8_t data[] = "12345678901234";
  //Serial.println(sizeof(data));
  nrf24.send(data, sizeof(data));
  //Serial.println((char*)nrf24._data3);
  nrf24.waitPacketSent();
  
  delay(10);
}
