rm -rf github
mkdir github
cd github
git clone git://github.com/dtstk/IoT_Acc
cd ..
rsync -av --progress github/IoT_Acc/cgateway/ cgateway --exclude config.json
cd cgateway
cd RF24
make install
cd ~/IoT_Acc/cgateway
make
chmod 777 gw.py
chmod 777 remote
chmod 777 register.py
chmod 777 init.py
chmod 777 remote.cpp
chmod 777 launcher.sh
cd ~/IoT_Acc/
cp github/IoT_Acc/update.sh update.sh -f -u
chmod 777 update.sh

