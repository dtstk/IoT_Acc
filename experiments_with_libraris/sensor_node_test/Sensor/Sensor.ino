#include <SPI.h>
#include <Mirf.h>
#include <nRF24L01.h>
#include <dht.h>
#include <MirfHardwareSpiDriver.h>

#define SCK_PIN 52
#define MISO_PIN 50
#define MOSI_PIN 51
#define LED 13
#define DHT11_PIN 2

dht DHT;
 
void setup(){
  Serial.begin(9600);
  Mirf.spi = &MirfHardwareSpi;  
  Mirf.cePin = 48;
  Mirf.csnPin = 49;   
  Mirf.init();  
//  Mirf.setTADDR((byte *)255); //To whom send data?
  Mirf.setTADDR((byte *)"serv");  
  Mirf.payload = 5;
  Mirf.channel = 1;  
  Mirf.config();
  
  Serial.println("Ready to send ..."); 
  pinMode(LED, OUTPUT);
}

void loop(){
  byte data[Mirf.payload];
  int chk = DHT.read11(DHT11_PIN);
  
  digitalWrite(LED, HIGH);
  data[0] = 1; //Sensor ID
  data[1] = (byte)DHT.temperature;
  data[2] = (byte)DHT.humidity;

  Mirf.send(data);   //Send the data back to the client.
  while(Mirf.isSending())
  {
    //Wait
  }
  digitalWrite(LED, LOW); 
  
  delay(1000+random(100));
}
