#include <iostream>
#include <string>
#include <stdarg.h>
#include "syslog.h"

#define LOG_STRING_LEN 128

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

		void log(const char *message, ...)
		{
            va_list vl;
            va_start(vl, message);
            vsnprintf(buf, sizeof( buf), message, vl);
			va_end(vl);

			syslog(logPriority, buf);
		}

        void logError(const char *message, ...)
        {
            va_list vl;
            va_start(vl, message);
            vsnprintf(buf, sizeof( buf), message, vl);
            va_end(vl);

            syslog(LOG_ERR, buf);
        }

        void logCrit(const char *message, ...)
        {
            va_list vl;
            va_start(vl, message);
            vsnprintf(buf, sizeof( buf), message, vl);
            va_end(vl);

            syslog(LOG_CRIT, buf);
        }

        void setLogLevel(int priority)
		{
			logPriority = priority;
		}

	private:
		int logPriority;
		char buf[LOG_STRING_LEN];

};
