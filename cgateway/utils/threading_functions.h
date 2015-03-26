struct cmdToThread{
	char cmd[100];
	int currentThreadId;
	int type;
};

void* collectGWDataAndSendToCloud(void *cmd);
