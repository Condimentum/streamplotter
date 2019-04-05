import os.path
import re
import json

## For plotting data
from matplotlib import pyplot as plt
import numpy as np

class Stream:
	def __init__(self, source, destination, port, direction, protocol, size):
		self.source = source
		self.destination = destination
		self.port = port
		self.direction = direction
		self.protocol = protocol
		self.size = size
		self.numOfPackets = 1
		self.process = ''

	def addPacket(self, size):
		self.numOfPackets += 1
		self.size += size

	def setProcess(self, process):
		self.process = process

	def getSource(self):
		return self.source

	def getDestination(self):
		return self.destination

	def __repr__(self):
		return str(self.__dict__)

def reformatIP(IP):
	k = IP.rfind(".")
	result = IP[:k] + ':' + IP[k+1:]
	return result

i = 1

while os.path.exists("netstat%s" % i) and os.path.exists("tcpdump%s" % i):
    netstat = open("netstat%s" % i, "r")
    tcpdump = open("tcpdump%s" % i, "r")
    streams = open("streams%s" % i, "w+")
    streamDict = {}
    proto = ""
    length = 0
    source = ""
    destination = ""
    for j, tcpline in enumerate(tcpdump):
    	try:
    		words = tcpline.split()
    		if j % 2 == 0:
    			proto = words[words.index("proto") + 1]
    			length = int(re.sub('\D', '', words[words.index("length") + 1]))
    			continue
    		source = reformatIP(words[0])
    		destination = reformatIP(re.sub(':', '', words[2]))
    		port = int(destination.split(':')[1])
    		direction = 'down'
    		if port <= 443:
    			port = int(source.split(':')[1])
    			direction = 'up'
    		# print(direction, port)
    		# print(source, proto, destination, length)
    		if source in streamDict:
    			streamDict[source].addPacket(length)
    		else:
    			streamDict[source] = Stream(source, destination, port, direction, proto, length)
    	except Exception as e: #print(e)
    		continue
    netstatContents = netstat.read().split();
    for k, v in streamDict.items():
    	localIP = v.destination
    	if v.direction == 'up':
    		localIP = v.source
    	try:
    		process = netstatContents[netstatContents.index(localIP) +3]
    	except Exception as e:
    		continue
    	v.setProcess(process)
    	stream = str(v)
    	streams.write(stream+"\n")
    netstat.close()
    tcpdump.close()
    i+=1