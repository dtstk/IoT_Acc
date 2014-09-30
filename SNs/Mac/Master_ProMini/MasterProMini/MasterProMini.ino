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


int interval;




void setup(){  
  Serial.begin(9600);
  
  interval = 10;
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
    if ( ( millis() - time ) > (interval*100 + 50) )
    {
      Serial.println("Timeout ...");
      return;
    }    
  }
  
  

 if(Mirf.dataReady())
 {
    Mirf.getData(data);
    Serial.print("Sensor #");
    Serial.print(data[0]);
  
    Serial.print("  Data byte 1-4: ");
    Serial.print(data[1]);
    Serial.print(", ");    
    Serial.print(data[2]);
    Serial.print(", ");    
    Serial.print(data[3]);
    Serial.print(", ");    
    Serial.println(data[4]);
    
    //Switching to TX
    Mirf.setTADDR((byte *)"cln1");
      
    data[0] = 255; //Sensor ID
    interval = random(5,50); //interval unit = 100ms
    data[1] = interval;
    Serial.print("New interval - ");
    Serial.println(interval);
    
    Mirf.send(data);
    while(Mirf.isSending())
    {
      //Wait
    }
 }
}
