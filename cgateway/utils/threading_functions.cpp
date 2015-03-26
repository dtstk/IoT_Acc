#include <cstring>
#include <string>
#include "threading_functions.h"
#include "iot_types.h"
#include "netutils.hpp"
#include "sysl.hpp"

extern NetworkingUtils net_utils;
extern Logger log;

void* collectGWDataAndSendToCloud(void *cmd)
{
	struct cmdToThread sNew;

	std::memcpy(&sNew, cmd, sizeof(cmdToThread));

	std::string temp(net_utils.getIPAdr(1));

	log.log(1, "INFO: Command in the Thread:%s\r\n", sNew.cmd);

	log.log(1, "INFO: Exiting the Thread Nr.%i\n\n", sNew.currentThreadId);

    return RET_OK;

}
