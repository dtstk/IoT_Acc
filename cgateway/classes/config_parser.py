import sys

class ConfigParser():
	def __init__():
		self.json_data=open('config.json')
		
	def getAzureSBService_namespace(self):
		try:
			return self.json_data["Azure_Services"]["servicebus"]["service_namespace"]
		except:
			print "Unexpected error:", sys.exc_info()[0]
		
	def getAzureSBShared_access_key_name(self):
		try:
			return self.json_data["Azure_Services"]["servicebus"]["shared_access_key_name"]
		except:
			print "Unexpected error:", sys.exc_info()[0]
	def getAzureSBShared_access_key_value(self):
		try:
			return self.json_data["Azure_Services"]["servicebus"]["shared_access_key_value"]
		except:
			print "Unexpected error:", sys.exc_info()[0]