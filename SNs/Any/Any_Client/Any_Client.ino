#include <BH1750.h>
#include <Wire.h>
#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"
#include "printf.h"
//#include <../mac.h>
#include <dht.h>

#define DELAY 20000
#define DHT11_S 2
#define PIR_DATA 4
#define SWITCH_CONTROL 5

int BH1750address = 0x23;
BH1750 LightSensor;

char NodeID[2] = "N";

// Set up nRF24L01 radio on SPI bus plus pins 9 & 10 
RF24 radio(9,10);
//7,10
//
// Topology
//

// Radio pipe addresses for the 2 nodes to communicate.
                        //Writing Pipe   //Command Listening //Registration Pipe
const uint64_t pipes[3] = { 0xF0F0F0F0E1LL, 0xF0F0F0F0D2LL, 0xF0F0F0F0D3LL };

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

  // optionally, increase the delay between retries & # of retries
  radio.setRetries(15,15);
  radio.setAutoAck(false);
  radio.setPALevel(RF24_PA_MAX);
  if (radio.setDataRate(RF24_250KBPS))
    printf("RF24_250KBPS has been set...\r\n");
  else
    printf("Failed with RF24_250KBPS setting...\r\n");
    
  //optionally, reduce the payload size.
  //radio.setPayloadSize(8);

  //
  // Open pipes to other nodes for communication
  //

  // This simple sketch opens two pipes for these two nodes to communicate
  // back and forth.
  // Open 'our' pipe for writing
  // Open the 'other' pipe for reading, in position #1 (we can have up to 5 pipes open for reading)

  //if ( role == role_ping_out )
  {
    //radio.openWritingPipe(pipes[0]);
    radio.openReadingPipe(0,pipes[0]);
    radio.openReadingPipe(1,pipes[1]);
  }
  //else
  {
    radio.openWritingPipe(pipes[1]);
    //radio.openReadingPipe(1,pipes[0]);
  }

  //
  // Start listening
  //

  radio.startListening();

  radio.printDetails();
  //role = role_ping_out;

  pinMode(PIR_DATA, INPUT);  
  pinMode(SWITCH_CONTROL, OUTPUT);
}

void loop(void)
{
  bool ok;
  char a[10];
     
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

//    // Wait here until we get a response, or timeout (250ms)
//    unsigned long started_waiting_at = millis();
//    bool timeout = false;
//    while ( ! radio.available() && ! timeout )
//      if (millis() - started_waiting_at > 200 )
//        timeout = true;
//
//    // Describe the results
//    if ( timeout )
//    {
//      printf("Failed, response timed out.\n\r");
//    }
//    else
//    {
//      // Grab the response, compare, and send to debugging spew
//      unsigned long got_time;
//      radio.read( &got_time, sizeof(unsigned long) );
//
//      // Spew it
//      printf("Got response %lu, round-trip delay: %lu\n\r",got_time,millis()-got_time);
//    }

    // Try again 1s later
  }


  if ( role == role_registration )
  {
      rest();

      int handshakeID;
      handshakeID = (int)random(1000);
      sprintf(a, "?");  
      sprintf(a + strlen(a), "r_v01_%03i", handshakeID);
      printf("Request Registration %s:", a);
  
      if (radio.write(a, sizeof(a)))
        printf("ok.\n\r");
      else
        printf("failed.\n\r");
        
      radio.startListening();
      delay(2000);      
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
   	  delay(200);
        }
      }

      // First, stop listening so we can talk
      radio.stopListening();          

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
  sprintf(a, NodeID);
  sprintf(a + strlen(a), "h_%02i", value);
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
  sprintf(a, NodeID);
  sprintf(a + strlen(a), "t_%02i", value);
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
  sprintf(a, NodeID);  
  sprintf(a + strlen(a), "l_%i", value);
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
  sprintf(a, NodeID);  
  sprintf(a + strlen(a), "p_%01i", value);
  printf("Now sending %s:", a);
    
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

