CC=gcc
CFLAGS= -lmosquitto

all: mqtt-broker.o
	$(CC) $(CFLAGS) -o mqtt-broker mqtt-broker.o

mqtt-broker.o:
	$(CC) $(CFLAGS) -c mqtt-broker.c

clean:
	rm mqtt-broker.o mqtt-broker