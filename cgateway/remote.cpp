#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <string>
#include <getopt.h>
#include <cstdlib>
#include <iostream>
#include "RF24/RF24.h"
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <net/if.h>
#include <arpa/inet.h>

#include "./classes/sysl.hpp"

using namespace std;

#define DEBUG 0
#define NUM_THREADS 20
#define CMD_LINE_MAX 100

Logger log("IoT_GW");

//RF24 radio("/dev/spidev0.0",8000000 , 25);  //spi device, speed and CSN,only CSN is NEEDED in RPI
RF24 radio(RPI_V2_GPIO_P1_22, RPI_V2_GPIO_P1_24, BCM2835_SPI_SPEED_1MHZ);
const int role_pin = 7;
const uint64_t pipes[2] = { 0xF0F0F0F0E1LL, 0xF0F0F0F0D2LL };

struct cmdToThread{
    char cmd[100];
    int currentThreadId;
    int type;
};

void setup(void){
	//Prepare the radio module
	printf("\nPreparing interface\n");
	log.log("Preparing interface");
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
	printf("\nFinished interface\nRadio Data Available:%s", radio.available()?"Yes":"No");
	log.log("Finished interface. Radio Data Available:%s", radio.available()?"Yes":"No");
	log.log("!!!!!!!!!!!!!!");
}

void getAndPrintIPAdr()
{
	int fd;
	struct ifreq ifr;

	fd = socket(AF_INET, SOCK_DGRAM, 0);

	/* I want to get an IPv4 IP address */
	ifr.ifr_addr.sa_family = AF_INET;

	/* I want IP address attached to "eth0" */
	strncpy(ifr.ifr_name, "eth0", IFNAMSIZ-1);

	ioctl(fd, SIOCGIFADDR, &ifr);

	close(fd);

 /* display result */
	printf("%s\n", inet_ntoa(((struct sockaddr_in *)&ifr.ifr_addr)->sin_addr));
}


void* sendDataToCloud(void *cmd)
{
	struct cmdToThread sNew;

	memcpy(&sNew, cmd, sizeof(cmdToThread));

	getAndPrintIPAdr(); 
	printf("Command in the Thread:%s\r\n", sNew.cmd);

//--------------------Some workaround on passing data from python------------------
//Another possibility is to: 
//1. utilize some IPC
//2. Study python executor for C
	printf("Command Type:%i\r\n", sNew.type);

	if(sNew.type == 2)
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
			perror("Error while opening the file.\n");
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
					         printf("Registration ID broadcast - ok.\n\r");
						else
							 printf("Registration ID broadcast - failed.\n\r");

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

	printf("\n\nExiting the Thread Nr.%i\n\n", sNew.currentThreadId);

	return NULL;
}

int main( int argc, char ** argv){

	//char choice;
    log.log("Program started");

	setup();
	//bool switched = false;
	//int counter = 0;
	pthread_t threads[NUM_THREADS];
	int nextThreadId = 0;

//Define the options

	radio.startListening();
	//Let's take the time while we listen
    //unsigned long started_waiting_at = millis();
    //bool timeout = false;
//    while ( ! radio.available() && ! timeout ) {
	while(1)
	{
		delayMicroseconds(40000);

		if(radio.available())
		{
			//printf("Radio Data Available!!!\n");
            char abc[100];
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

				s.type = 1;//data
				int err = pthread_create(&(threads[nextThreadId]), NULL, &sendDataToCloud, (void*)&s);
				pthread_detach(threads[nextThreadId]);

				if (err != 0)
					printf("\nCan't create thread :[%s]", strerror(err));
				else
					printf("\n Thread Nr.%i created!\n", s.currentThreadId);

				nextThreadId++;


				///////////////////////////////////////////////////////////////////////////////////////////
				////////////////////////         Sent to Carriot Platform            //////////////////////
				///////////////////////////////////////////////////////////////////////////////////////////	
/*
				struct cmdToThread s2; 

				snprintf(s2.cmd, sizeof(s2.cmd), "./carriots.py %s", abc);
				 
				if (nextThreadId >= NUM_THREADS)
					nextThreadId = 0;

				s2.currentThreadId = nextThreadId;

				int err2 = pthread_create(&(threads[nextThreadId]), NULL, &sendDataToCloud, (void*)&s2);
				pthread_detach(threads[nextThreadId]);

				if (err2 != 0)
					printf("\nCan't create thread :[%s]", strerror(err2));
				else
					printf("\n Thread Nr.%i created!\n", s2.currentThreadId);

				nextThreadId++;				
*/
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

                   sReg.type = 2;//reg
					int err = pthread_create(&(threads[nextThreadId]), NULL, &sendDataToCloud, (void*)&sReg);
					pthread_detach(threads[nextThreadId]);

					if (err != 0)
					  printf("\nCan't create thread :[%s]", strerror(err));
					else
					  printf("\n Thread Nr.%i created!\n", sReg.currentThreadId);

					nextThreadId++;
				}

                //unsigned long got_time;
                //radio.read( &got_time, sizeof(unsigned long) );
                //printf("Got response %lu, round-trip delay: \n\r",got_time);

                //delayMicroseconds(20*10);
                //radio.stopListening();

/*                
                //Send the message
                bool ok = radio.write( &(got_time), sizeof(unsigned long) );
                if (ok)
                    printf("ok...");
                else
                    printf("failed.\n\r");
                    //Listen for ACK
*/
                radio.startListening();
                delayMicroseconds(20*10);
            }
        }
}
