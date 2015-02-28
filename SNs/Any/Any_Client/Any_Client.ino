#include <BH1750.h>
#include <Wire.h>
#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"
#include "printf.h"
//#include <../mac.h>
#include <dht.h>
#include <EEPROM.h>

//Validation for Sensors changes each 20 sec
#define DELAY 3000
//Control Values = 90 times
#define RESET_Interval 250
#define DHT11_S 2
#define PIR_DATA 4
#define RESET_PIN 3
#define SWITCH_CONTROL 5
#define INDICATION_PIN 8

int BH1750address = 0x23;
BH1750 LightSensor;

int NodeID;

// Set up nRF24L01 radio on SPI bus plus pins 9 & 10 
RF24 radio(9,10);
//7,10
//
// Topology
//

// Radio pipe addresses for the 2 nodes to communicate.
                        //Writing Pipe   //Command Listening & Registration Pipe
const uint64_t pipes[2] = { 0xF0F0F0F0E1LL, 0xF0F0F0F0D2LL};

//
// Role management
//
// Set up role.  This sketch uses the same software for all the nodes
// in this system.  Doing so greatly simplifies testing.  
//

// The various roles supported by this sketch
typedef enum { role_ping_out = 1, role_pong_back = 2,  role_registration = 3 } role_e;

// The debug-friendly names of those roles
const char* role_friendly_name[] = { "invalid", "Ping out", "Pong back"};

// The role of the current running sketch
role_e role = role_ping_out;
//role_e role = role_registration;
dht DHT;


int m_temp = -1;
int m_humd = -1;
uint16_t m_lux = -1;
int m_pir = -1;
int i = 0;

void setup(void)
{
  Serial.begin(9600);
  LightSensor.begin(BH1750_CONTINUOUS_HIGH_RES_MODE);
  
  printf_begin();
  printf("\n\rRF24/examples/GettingStarted/\n\r");
  printf("ROLE: %s\n\r",role_friendly_name[role]);
  printf("*** PRESS 'T' to begin transmitting to the other node\n\r");

  //
  // Setup and configure rf radio
  //

  radio.begin();
  radio.setChannel(0x4c);  
  radio.setPALevel(RF24_PA_MAX);
  

  if (radio.setDataRate(RF24_250KBPS))
    printf("RF24_250KBPS has been set...\r\n");
  else
    printf("Failed with RF24_250KBPS setting...\r\n");
  radio.setAutoAck(false);
  // optionally, increase the delay between retries & # of retries  
  radio.setRetries(1,1);
    
  //optionally, reduce the payload size.
  //radio.setPayloadSize(8);

//  EEPROM_writelong(0,513);
  NodeID=(int)EEPROM_readlong(0);
  printf("DeviceId=%03i - Read from Memory\r\n", NodeID);

  radio.openReadingPipe(0,pipes[0]);
  radio.openWritingPipe(pipes[1]);
  radio.startListening();
  radio.printDetails();
  //role = role_ping_out;

  pinMode(PIR_DATA, INPUT);  
  digitalWrite(PIR_DATA, HIGH);
//  pinMode(SWITCH_CONTROL, OUTPUT);
//  pinMode(RESET_PIN, INPUT);
//  EEPROM_writelong(0,21);
//  pinMode(RESET_PIN, INPUT_PULLUP);
//  digitalWrite(RESET_PIN, LOW);
  pinMode(INDICATION_PIN, OUTPUT);

  randomSeed(analogRead(0));
}

void loop(void)
{
  bool ok;
  char a[10];

//  int resetPressed = digitalRead(RESET_PIN);
//  if (resetPressed == true )
//  {
//    role = role_registration;
//    digitalWrite(RESET_PIN, LOW);
//  }

  if (role == role_ping_out)
  {
    // First, stop listening so we can talk.
    rest();

    dealWithPIRData(a, sizeof(a));            
    rest();

    dealWithLuxData(a, sizeof(a));
    rest();
 
    if(checkDHT11() == DHTLIB_OK)
    {      
      dealWithHumData(a, sizeof(a));
      rest();

      dealWithTempData(a, sizeof(a));
      rest();      
    }

    // Now, continue listening
    
    delay(DELAY);
    i++;
    if (i>RESET_Interval) resetMeasurement();

  }


  if ( role == role_registration )
  {
      rest();

      int handshakeID;
      handshakeID = (int)random(998);
      printf("\n\r");
      printf("-----------------------------------\n\r");
      
      sprintf(a, "?");  
      sprintf(a + strlen(a), "r_v01_%03i", handshakeID);
      printf("Registration: Request %s:", a);
  
      if (radio.write(a, sizeof(a)))
        printf("ok.\n\r");
      else
        printf("failed.\n\r");
        
      radio.startListening();
      radio.stopListening();
      radio.startListening();      
      delay(20000);      
      if ( radio.available() )
      {
        // Dump the payloads until we've gotten everything
        unsigned long deviceIdReceived;
        bool done = false;
        while (!done)
        {
          // Fetch the payload, and see if this was the last one.
          radio.read( &deviceIdReceived, sizeof(unsigned long) );

          // Spew it
          if ((int)handshakeID==(int)deviceIdReceived)
          {
             /////NB assumption that we will use 4 bytes for data in eprom
             EEPROM_writelong(0,deviceIdReceived);
             NodeID=deviceIdReceived;                   
             printf("Registration: Mine Confirmation received %lu. \n\r",deviceIdReceived);
          }
          else
          {
             printf("Registration: Someone's confirmatino received %lu. \n\r",deviceIdReceived);
          }
        }
      }
      else
      {
         printf("Registration: NOTHING received, Connect +5V and D3 again. \n\r");
      }

      // First, stop listening so we can talk
      radio.stopListening();          
      
      role = role_ping_out;
  }

  //
  // Pong back role.  Receive each packet, dump it out, and send it back
  //

  if ( role == role_pong_back )
  {
    // if there is data ready
    if ( radio.available() )
    {
      // Dump the payloads until we've gotten everything
      unsigned long got_time;
      bool done = false;
      while (!done)
      {
        // Fetch the payload, and see if this was the last one.
        radio.read( &got_time, sizeof(unsigned long) );

        // Spew it
        printf("Got payload %lu...",got_time);

	// Delay just a little bit to let the other unit
	// make the transition to receiver
	delay(20);
      }

      // First, stop listening so we can talk
      radio.stopListening();

      // Send the final one back.
      radio.write( &got_time, sizeof(unsigned long) );
      printf("Sent response.\n\r");

      // Now, resume listening so we catch the next packets.
      radio.startListening();
    }
  }

  //
  // Change roles
  //

  if ( Serial.available() )
  {
    char c = toupper(Serial.read());
    if ( c == 'T' && role == role_pong_back )
    {
      printf("*** CHANGING TO TRANSMIT ROLE -- PRESS 'R' TO SWITCH BACK\n\r");

      // Become the primary transmitter (ping out)
      role = role_ping_out;
      radio.openWritingPipe(pipes[0]);
      radio.openReadingPipe(1,pipes[1]);
    }
    else if ( c == 'R' && role == role_ping_out )
    {
      printf("*** CHANGING TO RECEIVE ROLE -- PRESS 'T' TO SWITCH BACK\n\r");
      
      // Become the primary receiver (pong back)
      role = role_pong_back;
      radio.openWritingPipe(pipes[1]);
      radio.openReadingPipe(1,pipes[0]);
    }
  }
}

int checkDHT11(void)
{
  int chk = DHT.read11(DHT11_S);
  switch (chk)
  {
    case DHTLIB_OK:  
      Serial.print("DHT11 Sensor is OK."); 
      break;
    case DHTLIB_ERROR_CHECKSUM: 
      Serial.print("Checksum error!"); 
      break;
    case DHTLIB_ERROR_TIMEOUT: 
      Serial.print("Time out error!"); 
      break;
    default: 
      Serial.print("Unknown error!"); 
      break;
  }
  return chk;
}

int dealWithHumData(char* a, unsigned int aLen)
{
  int value = (int)DHT.humidity;
  sprintf(a, "%03i", NodeID);
  sprintf(a + strlen(a), "_h_%02i", value);
  printf("Now sending %s:", a);
    
  if (m_humd != value)  
  {
    if (radio.write(a, aLen))
      printf("ok.\n\r");
    else
      printf("failed.\n\r");
      
      m_humd = value;
  }    
  else
  {
     printf("No changes.\r\n");
  }
  
  return value;    
}

int dealWithTempData(char* a, unsigned int aLen)
{
  int value = (int)DHT.temperature;
  sprintf(a, "%03i", NodeID);
  sprintf(a + strlen(a), "_t_%02i", value);
  printf("Now sending %s:", a);
    
  if (m_temp != value)  
  {
    if (radio.write(a, aLen))
      printf("ok, ");
    else
      printf("failed, ");  
      
    m_temp = value;      
  }
  else
  {
     printf("No changes.\r\n");
  }
  
  return value;
}

uint16_t dealWithLuxData(char* a, unsigned int aLen)
{
  uint16_t value = LightSensor.readLightLevel();
  sprintf(a, "%03i", NodeID);
  sprintf(a + strlen(a), "_l_%i", value);
  printf("Now sending %s:", a);
    
  if (m_lux != value)  
  {
    if ((value>=0)&&(value<=5000))
    {
      if (radio.write(a, aLen))
        printf("ok.\n\r");
      else
        printf("failed.\n\r"); 
    }
    else
    {
        printf("Not Connected.\n\r"); 
    }
    
    m_lux = value;      
  }
  else
  {
     printf("No changes.\r\n");
  }
  
  return value;
}

bool dealWithPIRData(char* a, unsigned int aLen)
{
  int value = digitalRead(PIR_DATA);
  sprintf(a, "%03i", NodeID);
  sprintf(a + strlen(a), "_p_%01i", value);
  printf("Now sending %s:", a);

  digitalWrite(INDICATION_PIN, value); 
  
  if (m_pir != value)  
  {
    if (radio.write(a, aLen))
      printf("ok.\r\n");
    else
      printf("failed.\n\r");
      
    m_pir = value;            
  }
  else
  {
     printf("No changes.\r\n");
  }
    
  return value;
}

void rest()
{
  radio.startListening();
  radio.stopListening();
}

void resetMeasurement()
{
  m_temp = -1;
  m_humd = -1;
  m_lux = -1;
  m_pir = -1;
  i = 0;
  printf("Refresh values\n\r");
}


 

  // read double word from EEPROM, give starting address
unsigned long EEPROM_readlong(int address) {
  //use word read function for reading upper part
  unsigned long dword = EEPROM_readint(address);
  //shift read word up
  dword = dword << 16;
  // read lower word from EEPROM and OR it into double word
  dword = dword | EEPROM_readint(address+2);
  return dword;
}

//write word to EEPROM
void EEPROM_writeint(int address, int value) {
  EEPROM.write(address,highByte(value));
  EEPROM.write(address+1 ,lowByte(value));
}
  
  //write long integer into EEPROM
void EEPROM_writelong(int address, unsigned long value) {
  //truncate upper part and write lower part into EEPROM
  EEPROM_writeint(address+2, word(value));
  //shift upper part down
  value = value >> 16;
  //truncate and write
  EEPROM_writeint(address, word(value));
}

unsigned int EEPROM_readint(int address) {
  unsigned int word = word(EEPROM.read(address), EEPROM.read(address+1));
  return word;
}

