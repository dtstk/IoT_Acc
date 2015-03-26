#include <stdio.h>
#include <stdlib.h>

#include <string.h>
#include <iostream>

#include <net/if.h>
#include <netinet/in.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <arpa/inet.h>

#include "netutils.hpp"
#include "sysl.hpp"

#include <sys/types.h>
#include <ifaddrs.h>

extern Logger log;

std::string NetworkingUtils::getIPAdr(bool toReturn, std::string returnString)
{
	struct ifaddrs *addrs,*tmp;

	getifaddrs(&addrs);
	tmp = addrs;

	while (tmp)
	{
	    if (tmp->ifa_addr && tmp->ifa_addr->sa_family == AF_PACKET)
	    {
			int fd;
			struct ifreq ifr;

			fd = socket(AF_INET, SOCK_DGRAM, 0);
			/* I want to get an IPv4 IP address */
			ifr.ifr_addr.sa_family = AF_INET;
			/* I want IP address attached to "eth0" */
			strncpy(ifr.ifr_name, tmp->ifa_name, IFNAMSIZ-1);
			ioctl(fd, SIOCGIFADDR, &ifr);
			close(fd);

			returnString += tmp->ifa_name + std::string(": ") + inet_ntoa(((struct sockaddr_in *)&ifr.ifr_addr)->sin_addr) + " ";
	    }

    	tmp = tmp->ifa_next;
	}

	freeifaddrs(addrs);
	log.log(1, "IP addresses: %s\n", returnString.c_str());

	if(toReturn)
	{
		return returnString;
	}
	else
		return "";
}


//int main(void)
//{

//  printf ("Hello!");
//  Utils utils;

//  utils.getAndPrintIPAdr();

//  return 0;
//}
