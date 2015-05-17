sudo chmod 755 gw_launcher.sh
sudo cp ./gw_launcher.sh /etc/init.d
	
#TODO: To make the Raspberry Pi use your init script at the right time, one more step is required: running the command sudo update-rc.d myservice.sh defaults. This command adds in symbolic links to the /etc/rc.x directories so that the init script is run at the default times. you can see these links if you do ls -l /etc/rc?.d/*myservice.sh