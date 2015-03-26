#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <string>
#include <getopt.h>
#include <cstdlib>
#include <ctime>
#include <iostream>
#include "RF24/RF24.h"
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <net/if.h>
#include <arpa/inet.h>
#include <sstream>

#include "./utils/sysl.hpp"
#include "./utils/netutils.hpp"
#include "./utils/iot_types.h"
#include "./utils/threading_functions.h"

using namespace std;

#define DEBUG 0
#define NUM_THREADS 20
#define CMD_LINE_MAX 100

Logger log("IoT_GW");
NetworkingUtils net_utils;

//RF24 radio("/dev/spidev0.0",8000000 , 25);  //spi device, speed and CSN,only CSN is NEEDED in RPI
RF24 radio(RPI_V2_GPIO_P1_22, RPI_V2_GPIO_P1_24, BCM2835_SPI_SPEED_1MHZ);
const int role_pin = 7;
const uint64_t pipes[2] = { 0xF0F0F0F0E1LL, 0xF0F0F0F0D2LL };

void setup(void){
	//Prepare the radio module
	log.log(1, "INFO: Preparing interface");
	radio.begin();
	radio.setChannel(0x4c);
	radio.setPALevel(RF24_PA_MAX);

	radio.setDataRate(RF24_250KBPS);
	radio.setAutoAck(false);
	radio.setRetries( 1, 1);

	radio.openReadingPipe(0,pipes[1]);
	radio.openWritingPipe(pipes[0]);

	radio.startListening();
	radio.printDetails();
	log.log(1, "INFO: Finished interface. Radio Data Available: %s", radio.available()?"Yes":"No");

	net_utils.getIPAdr(0);
}

void* sendDataToCloud(void *cmd)
{
	struct cmdToThread sNew;

	memcpy(&sNew, cmd, sizeof(cmdToThread));

//	net_utils.getAndPrintIPAdr();
//	log.log(1, "INFO: Command in the Thread:%s\r\n", sNew.cmd);

//--------------------Some workaround on passing data from python------------------
//Another possibility is to: 
//1. utilize some IPC
//2. Study python executor for C
	//printf("Command Type:%i\r\n", sNew.type);
	log.log(1, "INFO: Command Type:%i\r\n", sNew.type);

	if(sNew.type == REGISTER_NEW_DEVICE_MSG)
	{
		char temp[1024];
		const char strToSearch[] = "Device Handshake ID=";

		sprintf(temp, "%s > temp%i.dat", sNew.cmd, sNew.currentThreadId);

		system(temp);

		sprintf(temp, "cat temp%i.dat | grep '%s' > regTemp%i.dat", sNew.currentThreadId, strToSearch, sNew.currentThreadId);
		system(temp);

		sprintf(temp, "regTemp%i.dat", sNew.currentThreadId);

		FILE *regID = fopen(temp, "r");

		if( regID == NULL )
		{
			//perror("Error while opening the file.\n");
			log.logError(1, "ERROR: Error while opening the file.");
			exit(EXIT_FAILURE);
		}

		//Assuming that file should be one liner
		char tempLine[512];
		if ( fgets (tempLine, sizeof(tempLine)-1, regID) != NULL ) 
		{
			if (strstr(tempLine, strToSearch) != NULL)
			{
				char * pch = tempLine;
				for (unsigned int i=0; i<strlen(tempLine); i++, pch++)
				{
					if (tempLine[i] == '=')
					{
						char idNumber[10];
						sprintf(idNumber, "%s", pch+1);

						int registrationId = atoi(idNumber);
						cout << "idNumber: |" << registrationId << "|\n";

						fclose(regID);

						char a[10];
						sprintf(a, "%03i", registrationId);
						radio.stopListening();
						if (radio.write(a, sizeof(a)))
						{
							//printf("Registration ID broadcast - ok.\n\r");
							log.log(1, "INFO: Registration ID broadcast - ok.");
						}
						else
						{
							//printf("Registration ID broadcast - failed.\n\r");
							log.logError(1, "ERROR: Registration ID broadcast - failed.");
						}

						delayMicroseconds(1000);
						radio.startListening();
						break;
					}
				}
			}
		}

		sprintf(temp, "rm temp%i.dat regTemp%i.dat", sNew.currentThreadId, sNew.currentThreadId);
		system(temp);
//--------------------------------------------------------------------------------
	}
	else
	{
		system(sNew.cmd);
	}

	//printf("\n\nExiting the Thread Nr.%i\n\n", sNew.currentThreadId);
	log.log(1, "INFO: Exiting the Thread Nr.%i\n\n", sNew.currentThreadId);

	return NULL;
}

int create_raspberry_cfg_stat_send_thread (pthread_t *threads, int *nextThreadId)
{
	struct cmdToThread s;

	//TODO: Here we should call a thread function to collect all GW-related data in it and send it to the cloud.
	//snprintf(s.cmd, sizeof(s.cmd), "./gw.py %s", data);

	if (*nextThreadId >= NUM_THREADS)
		*nextThreadId = 0;

	//cout << "nextThreadId" << nextThreadId;
	ostringstream oss;
	oss << "nextThreadId" << nextThreadId << "\r\n";
	cout << oss.str();

	s.currentThreadId = *nextThreadId;
	s.type = GATEWAY_SERVICE_DATA_MSG;
	strncpy(s.cmd, "Null", sizeof(s.cmd)-1);

	int err = pthread_create(&(threads[*nextThreadId]), NULL, &collectGWDataAndSendToCloud, (void*)&s);
	pthread_detach(threads[*nextThreadId]);

	if (err != 0)
		log.logError(1, "ERROR: Can't create thread :[%s]", strerror(err));
	else
		log.log(1, "INFO: Thread Nr.%i created!\n", s.currentThreadId);

	(*nextThreadId)++;

	return RET_OK;
}

int main( int argc, char ** argv)
{
	//TODO: Replace this parameter with configuration parameter
	int32_t GW_info_send_timeout = 5; //5 seconds
	time_t base_time;

	log.log(1, "INFO: Program started");

	setup();

	pthread_t threads[NUM_THREADS];
	int nextThreadId = 0;

	radio.startListening();

	base_time = time(nullptr);

	while(1)
	{
		if(time(nullptr) >= base_time+GW_info_send_timeout)
		{
			base_time = time(nullptr);

			ostringstream oss;
			oss << GW_info_send_timeout << " seconds passed\r\n";
			cout << oss.str();

			//TODO: Finish this method by sending all GW-related info to the Azure.

			//create_raspberry_cfg_stat_send_thread(threads, &nextThreadId);

			//oss << "nextThreadId:|" << nextThreadId << "|\r\n";
			//cout << oss.str();
		}

		delayMicroseconds(40000);
		//printf(".....\r\n");

		if(radio.available())
		{
			char abc[100];

			log.log(1, "INFO: Radio Data Available!\n");
			radio.read( abc, sizeof(abc) );

#if (DEBUG == 1)
			printf(abc, "?_v1_346");
#endif

			if (abc[0] != '?')
			{
				///////////////////////////////////////////////////////////////////////////////////////////
				////////////////////////         Sent to IoT Platform                //////////////////////
				///////////////////////////////////////////////////////////////////////////////////////////
				struct cmdToThread s; 

				//printf("Got response %s, round-trip delay: \n\r", abc);
				snprintf(s.cmd, sizeof(s.cmd), "./gw.py %s", abc);

				if (nextThreadId >= NUM_THREADS)
					nextThreadId = 0;

				s.currentThreadId = nextThreadId;
				s.type = SENSOR_DATA_MSG;//data

				int err = pthread_create(&(threads[nextThreadId]), NULL, &sendDataToCloud, (void*)&s);
				pthread_detach(threads[nextThreadId]);

				if (err != 0)
					//printf("\nCan't create thread :[%s]", strerror(err));
					log.logError(1, "ERROR: Can't create thread :[%s]", strerror(err));
				else
					//printf("\n Thread Nr.%i created!\n", s.currentThreadId);
					log.log(1, "INFO: Thread Nr.%i created!\n", s.currentThreadId);

				nextThreadId++;
			}
			else
			{
					///////////////////////////////////////////////////////////////////////////////////////////
					////////////////////////      Sent to IoT Platform for registration  //////////////////////
					///////////////////////////////////////////////////////////////////////////////////////////
					struct cmdToThread sReg; 

					//printf("Got response %s, round-trip delay: \n\r", abc);
					snprintf(sReg.cmd, sizeof(sReg.cmd), "./register.py %s", abc);

					if (nextThreadId >= NUM_THREADS)
					  nextThreadId = 0;

					sReg.currentThreadId = nextThreadId;
					sReg.type = REGISTER_NEW_DEVICE_MSG;//reg

					int err = pthread_create(&(threads[nextThreadId]), NULL, &sendDataToCloud, (void*)&sReg);
					pthread_detach(threads[nextThreadId]);

					if (err != 0)
						log.logError(1, "ERROR: Can't create thread :[%s]", strerror(err));
					else
						log.log(1, "INFO: Thread Nr.%i created!\n", sReg.currentThreadId);

					nextThreadId++;
			}

			radio.startListening();
			delayMicroseconds(20*10);
		}
	}
}
