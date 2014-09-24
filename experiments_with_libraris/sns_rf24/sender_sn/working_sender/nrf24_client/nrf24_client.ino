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

#define SENSOR_NODE_ID 2
// Singleton instance of the radio driver
//RH_NRF24 nrf24;
 RH_NRF24 nrf24(9, 10); // use this to be electrically compatible with Mirf
// RH_NRF24 nrf24(8, 10);// For Leonardo, need explicit SS pin
// RH_NRF24 nrf24(8, 7); // For RFM73 on Anarduino Mini

void setup() 
{
  Serial.begin(9600);
  while (!Serial) 
    ; // wait for serial port to connect. Needed for Leonardo only
  if (!nrf24.init())
    Serial.println("init failed");
  // Defaults after init are 2.402 GHz (channel 2), 2Mbps, 0dBm
  if (!nrf24.setChannel(1))
    Serial.println("setChannel failed");
  if (!nrf24.setRF(RH_NRF24::DataRate2Mbps, RH_NRF24::TransmitPower0dBm))
    Serial.println("setRF failed");    
  
  nrf24.printRegisters(); 
  pinMode(8, INPUT);      // sets the digital pin 7 as input
}


void loop()
{
  Serial.println("Sending to nrf24_server");
  // Send a message to nrf24_server
  char data[50];
  uint8_t data_[50]={0};
  int val = digitalRead(8);   // read the input pin
  int i;
  
  snprintf(data, sizeof(data), "%i|%i", SENSOR_NODE_ID, val);
  Serial.println(data);
  for(i=0; i<strlen(data); i++)
  {
    data_[i] = data[i]; 
  }
  data_[++i] = 0;
  
  nrf24.send(data_, i);
  
  nrf24.waitPacketSent();
  // Now wait for a reply
  uint8_t buf[RH_NRF24_MAX_MESSAGE_LEN];
  uint8_t len = sizeof(buf);

  if (nrf24.waitAvailableTimeout(500))
  { 
    // Should be a reply message for us now   
    if (nrf24.recv(buf, &len))
    {
      Serial.print("got reply: ");
      Serial.println((char*)buf);
    }
    else
    {
      Serial.println("recv failed");
    }
  }
  else
  {
    //Serial.println("No reply, is nrf24_server running?");
    Serial.print(".");
  }
  //sprintf(a, "8th pin status:%i", val);
  //Serial.println(data);
  delay(400);
}

