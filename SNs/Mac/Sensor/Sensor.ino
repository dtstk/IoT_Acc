#include <SPI.h>
#include <Mirf.h>
#include <nRF24L01.h>
//#include <dht.h>
#include <MirfHardwareSpiDriver.h>

#define SCK_PIN 52
#define MISO_PIN 50
#define MOSI_PIN 51
#define LED 13
#define DHT11_PIN 2

//dht DHT;


int interval;



 
void setup(){
  Serial.begin(9600);
  
  interval = 1000;
  
  Mirf.spi = &MirfHardwareSpi;  
  Mirf.cePin = 48;
  Mirf.csnPin = 49;   
  Mirf.init();  
  Mirf.setRADDR((byte *)"cln1"); //Self address
  Mirf.setTADDR((byte *)"serv"); //To whom send data?
  Mirf.payload = 5;
  Mirf.channel = 1;  
  Mirf.config();
  
  Serial.println("Ready to send ..."); 
  pinMode(LED, OUTPUT);
}







void loop(){
  byte data[Mirf.payload];  
//  int chk = DHT.read11(DHT11_PIN);
  
  Mirf.setTADDR((byte *)"serv"); 
  digitalWrite(LED, HIGH);
  data[0] = 1; //Sensor ID
//  data[1] = (byte)DHT.temperature;
//  data[2] = (byte)DHT.humidity;
  data[1] = 110 + random(9);
  data[2] = 120 + random(9);
  data[3] = 130 + random(9);
  data[4] = 140 + random(9);  


  Mirf.send(data);   //Send the data back to the client.
  unsigned long time = millis();
  while(Mirf.isSending())
  {
    //Wait
  }
  digitalWrite(LED, LOW); 
  
  
  
  while(!Mirf.dataReady())
  {
    //Wait for data
    if ( ( millis() - time ) > interval )
    {
      Serial.println("No data received. Switching to TX");
      return;
    }
  }

  if(Mirf.dataReady())
  {
    Mirf.getData(data);
    if ( (data[0] == 255) ) //Process only data from Master (ID = 255)
    if ( data[1] > 1 ) //check if interval is correct
    if ( interval != data[1])
    {
      interval = data[1]*100;
      Serial.print("New interval - ");
      Serial.print(interval);
      Serial.println(" set. Switching to TX");
    }
  }
  
  if ( ( millis() - time ) < interval ) delay(interval-( millis() - time ));

}
