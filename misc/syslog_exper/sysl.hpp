#include <iostream>
#include <string>
#include "syslog.h"

class Logger
{
	public:
		Logger():
			logPriority(LOG_INFO)
		{
			std::cout << "Logger Started...\n";
			openlog(NULL, LOG_CONS|LOG_NDELAY|LOG_PID, LOG_USER); 
		}

        Logger(const char* progName):
            logPriority(LOG_INFO)
        {
            openlog(progName, LOG_CONS|LOG_NDELAY|LOG_PID, LOG_USER);
        }

		~Logger()
		{
			closelog();
		}

		void log(const char* message)
		{
			syslog(logPriority, message);
		}

        void logError(const char* message)
        {
            syslog(LOG_ERR, message);
        }

        void logCrit(const char* message)
        {
            syslog(LOG_CRIT, message);
        }

        void setLogLevel(int priority)
		{
			logPriority = priority;
		}

	private:
		int logPriority;

};
