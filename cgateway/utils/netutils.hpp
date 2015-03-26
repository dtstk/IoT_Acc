//#include <sys/socket.h>


class NetworkingUtils
{
	public:
		NetworkingUtils()
		{
			;
		}

		std::string getIPAdr(bool toReturn, std::string returnString = "");
};
