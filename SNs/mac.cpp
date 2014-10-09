#include <mac.h>

long randNumber;

bool mac_send (char* buf, uint8_t len)
{
  randomSeed(analogRead(0));
  randNumber = random(300);
  delay(randNumber);
  
  
  return true;
}