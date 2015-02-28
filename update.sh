sudo rm -rf github
sudo mkdir github
cd github
sudo git clone git://github.com/dtstk/IoT_Acc
cd ..
sudo rsync -av --progress github/IoT_Acc/cgateway/ cgateway --exclude config.json
cd cgateway
cd RF24
sudo make install
cd ..
sudo g++ -Ofast -mfpu=vfp -mfloat-abi=hard -march=armv6zk -mtune=arm1176jzf-s -pthread -Wall -I../ -lrf24-bcm remote.cpp ./utils/netutils.cpp -o remote
sudo chmod 777 gw.py
sudo chmod 777 remote
sudo chmod 777 register.py
sudo chmod 666 remote.cpp
cd ..

