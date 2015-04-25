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

const char timed_out[] = "Time out error!\r\n";
const char checksum_err[] = "Checksum error!\r\n";

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
// state management
//
// Set up state.  This sketch uses the same software for all the nodes
// in this system.  Doing so greatly simplifies testing.  
//

// The various states supported by this sketch
typedef enum { state_ping_out = 1, state_pong_back = 2,  state_registration = 3 , state_initial = 4, receive_data = 5} state_e;

// The debug-friendly names of those states
const char* state_friendly_name[] = { "invalid", "Ping out", "Pong back", "Registration", "Initial State", "Receiving Data State"};

// The state of the current running sketch
//state_e state = state_ping_out;
state_e state = state_initial;
dht DHT;


int m_temp = -1;
int m_humd = -1;
uint16_t m_lux = -1;
int m_pir = -1;
int i = 0;

void setup(void)
{
  //TODO: Put the same code as from pingpairs Example.
  //TODO: Do not forget about: 
  //radio.setAutoAck(1);
  
  Serial.begin(9600);
  LightSensor.begin(BH1750_CONTINUOUS_HIGH_RES_MODE);
  
  printf_begin();
  printf("\n\rRF24/examples/GettingStarted/\n\r");
  printf("STATE: %s\n\r",state_friendly_name[state]);
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
  radio.setAutoAck(true);
  // optionally, increase the delay between retries & # of retries  
  radio.setRetries(15, 15);
    
  //optionally, reduce the payload size.
  //radio.setPayloadSize(8);

//  radio.openReadingPipe(0,pipes[0]);
//  radio.openWritingPipe(pipes[1]);
  radio.openWritingPipe(pipes[0]);
  radio.openReadingPipe(1,pipes[1]);
  radio.startListening();
  radio.printDetails();
  //state = state_ping_out;

//  EEPROM_writelong(0,513);
  NodeID=(int)EEPROM_readlong(0);
  printf("DeviceId=%03i - Read from Memory\r\n", NodeID);
  
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

#define MAX_RETRY_COUNT 30
#define RETRY_TIMEOUT 1000

const char trying[] = "Trying with NodeID restored from EEPROM\r\n";

void loop(void)
{
  bool ok;
  char a[10];
  char abc[20];

//TODO: State Machine

  if ( state == state_initial )
  {
    radio.stopListening();
    state = state_registration;
  }

  if ( state == state_registration )
  {
      rest();

      int handshakeID;
      if(NodeID)
      {
        printf("%s", trying);
        handshakeID = NodeID;
      }
      else
        handshakeID = (int)random(998);
        
      printf("\n\r");
      printf("-----------------------------------\n\r");
      
      sprintf(a, "?");  
      sprintf(a + strlen(a), "r_v01_%03i", handshakeID);
      printf("Registration: Request %s:", a);
      
      bool mineIDConfirmation = false;
      while (!mineIDConfirmation)
      {
        int retrycount = 0;
        
        rest();
        delay(RETRY_TIMEOUT);
        
        if (radio.write(a, sizeof(a)))
          printf("ok.");
        else
        {
          printf(".");
          continue;
        }

        printf("\n\r");

        radio.startListening();
      
        printf("Starting registartion with ID:%i\r\n", handshakeID);
        
        while (!radio.available())
        {        
          delay(RETRY_TIMEOUT);
          if(++retrycount > MAX_RETRY_COUNT)
            break;
          printf("Registration: NOTHING received (%i out of %i) \n\r", retrycount, MAX_RETRY_COUNT);
        }
      
        if(retrycount > MAX_RETRY_COUNT)
        {
          printf("Let's go for another registration request round\r\n");
          continue;
        }
        
        // Fetch the payload, and see if this was the last one.
        
        radio.read( abc, sizeof(abc) );
        printf("Received: %s\r\n", abc);
        
        // Dump the payloads until we've got everything
        unsigned long deviceIdReceived = atoi(abc);
  
        // Spew it
        if ((int)handshakeID==(int)deviceIdReceived)
        {
           /////NB assumption that we will use 4 bytes for data in eprom
           EEPROM_writelong(0,deviceIdReceived);
           NodeID=deviceIdReceived;
           printf("Registration: Mine Confirmation received %lu. \n\r",deviceIdReceived);
           mineIDConfirmation = true;           
           
           state = state_ping_out;
           break;
        }
        else
        {
           printf("Registration: Someone's confirmatino received %lu. \n\r",deviceIdReceived);
           state = state_initial;
        }
      }
      // First, stop listening so we can talk
      radio.stopListening();          
  }

  if (state == state_ping_out)
  {
    printf("Starting Data Send Procedure.\r\n");
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
    state = receive_data;
    
  }//if (state == state_ping_out)
  
  
  
  if (state == receive_data)
  {
    int retrycount = 0;
    
    rest();
    delay(RETRY_TIMEOUT);
    
    printf("\r\nSending Data reception ready notification.\r\n");
    snprintf(a, sizeof(a), "!d_v01_%03i", NodeID);
    
    retrycount = 0;
    while (!radio.write(a, sizeof(a)))
    {
      delay(RETRY_TIMEOUT);
      if(++retrycount > MAX_RETRY_COUNT)
        break;
      printf(".");
    }
    
    retrycount = 0;
    printf("ok.");

    printf("\n\r");

    radio.startListening();
  
    printf("Starting Receiving.\r\n");
    
    while (!radio.available())
    {        
      delay(RETRY_TIMEOUT);
      if(++retrycount > MAX_RETRY_COUNT)
        break;
      printf("Received: NOTHING (%i out of %i) \n\r", retrycount, MAX_RETRY_COUNT);
    }
  
    if(retrycount > MAX_RETRY_COUNT)
    {
      printf("Let's go for another data transmission cycle.\r\n");
      state = state_ping_out;
//      resetMeasurement();
    }
    else
    {
      // Fetch the payload, and see if this was the last one.
//      char abc[20];
      radio.read( abc, sizeof(abc) );
      printf("Received: %s\r\n", abc);
    }
  }//if (state == receive_data)
  
  
  //
  // Pong back state.  Receive each packet, dump it out, and send it back
  //

  if ( state == state_pong_back )
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
}

int checkDHT11(void)
{
  int chk = DHT.read11(DHT11_S);
  switch (chk)
  {
    case DHTLIB_OK:  
      printf("DHT11 Sensor is OK.\r\n"); 
      break;
    case DHTLIB_ERROR_CHECKSUM: 
      printf("%s", checksum_err); 
      break;
    case DHTLIB_ERROR_TIMEOUT: 
      printf("%s", timed_out); 
      break;
    default: 
      printf("Unknown error!\r\n"); 
      break;
  }
  return chk;
}

int dealWithHumData(char* a, unsigned int aLen)
{
  int value = (int)DHT.humidity;
  sprintf(a, "%03i", NodeID);
  sprintf(a + strlen(a), "_h_%02i", value);
  printf("Now sending \"HumData\": %s:", a);
    
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
  printf("Now sending \"TempData\": %s:", a);
    
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
  
//  if (m_pir != value)  
  {
    if (radio.write(a, aLen))
      printf("ok.\r\n");
    else
      printf("failed.\n\r");
      
    m_pir = value;            
  }
//  else
//  {
//     printf("No changes.\r\n");
//  }
    
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

