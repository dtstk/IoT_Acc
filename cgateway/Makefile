TARGET=remote
CC=g++
ODIR=obj
CFLAGS=-Ofast -std=c++0x -mfpu=vfp -mfloat-abi=hard -march=armv6zk -mtune=arm1176jzf-s -Wall
LIBS=-lrf24-bcm -pthread


all: remote

$(TARGET): threading_functions.o $(TARGET).o
	$(CC) $(CFLAGS) $(LIBS) remote.o threading_functions.o -o $(TARGET)

$(TARGET).o: $(TARGET).cpp
	$(CC) -c $(CFLAGS) remote.cpp

threading_functions.o: ./utils/threading_functions.cpp
	$(CC) -c $(CFLAGS) ./utils/threading_functions.cpp

clean: 
	rm -rf *.o remote
