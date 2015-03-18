TARGET=remote
CC=g++
ODIR=obj
CFLAGS=-Ofast -std=c++0x -mfpu=vfp -mfloat-abi=hard -march=armv6zk -mtune=arm1176jzf-s -Wall
LIBS=-lrf24-bcm -pthread


all: remote

$(TARGET): netutils.o $(TARGET).o
	$(CC) $(CFLAGS) $(LIBS) remote.o netutils.o -o $(TARGET)

$(TARGET).o: $(TARGET).cpp
	$(CC) -c $(CFLAGS) remote.cpp

netutils.o: ./utils/netutils.cpp
	$(CC) -c $(CFLAGS) ./utils/netutils.cpp

clean: 
	rm -rf *.o remote
