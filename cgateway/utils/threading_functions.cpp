#include <cstring>
#include <string>
#include "threading_functions.h"
#include "iot_types.h"
#include "sysl.hpp"

extern Logger logProcess;

void* collectGWDataAndSendToCloud(void *cmd)
{
	struct cmdToThread sNew;

	std::memcpy(&sNew, cmd, sizeof(cmdToThread));

	logProcess.log(1, "INFO: Command in the Thread:%s\r\n", sNew.cmd);
	logProcess.log(1, "INFO: Exiting the Thread Nr.%i\n\n", sNew.currentThreadId);

    return RET_OK;

}
