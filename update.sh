sudo rm -rf github
sudo mkdir github
cd github
sudo git clone git://github.com/dtstk/IoT_Acc
cd ..
sudo rsync -av --progress github/IoT_Acc/cgateway/ cgateway --exclude config.json
cd cgateway
cd RF24
sudo make install
cd ~/IoT_Acc/cgateway
sudo make
sudo chmod 777 gw.py
sudo chmod 777 remote
sudo chmod 777 register.py
sudo chmod 777 init.py
sudo chmod 777 remote.cpp
sudo chmod 777 launcher.sh
cd ~/IoT_Acc/
cp github/IoT_Acc/update.sh update.sh -f -u
sudo chmod 777 update.sh

