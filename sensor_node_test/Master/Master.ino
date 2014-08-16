/**
 * A Mirf example to test the latency between two Ardunio.
 *
 * Pins:
 * Hardware SPI:
 * MISO -> 12
 * MOSI -> 11
 * SCK -> 13
 *
 * Configurable:
 * CE -> 8
 * CSN -> 7
 *
 * Note: To see best case latency comment out all Serial.println
 * statements not displaying the result and load 
 * 'ping_server_interupt' on the server.
 */

#include <SPI.h>
#include <Mirf.h>
#include <nRF24L01.h>
#include <MirfHardwareSpiDriver.h>

void setup(){  
  Serial.begin(9600);
  Mirf.spi = &MirfHardwareSpi;
  Mirf.init();
  Mirf.setRADDR((byte *)"serv");
  Mirf.payload = 5;
  Mirf.channel = 1;
  Mirf.config();  

  Serial.println("Ready to receive ... "); 
}

void loop(){
  byte data[Mirf.payload];
  unsigned long time = millis();

  while(!Mirf.dataReady())
  {
    //Wait for data
    if ( ( millis() - time ) > 1500 ) {
      Serial.println("Timeout ...");
      return;
    }    
  }

  Mirf.getData(data);
  Serial.print("Sensor #");
  Serial.print(data[0]);
  
  Serial.print("  temperature - ");
  Serial.print(data[1]);
  
  Serial.print(" (C),  humidity - ");
  Serial.print(data[2]);
  Serial.println("(%RH)");
} 
  
  
  
