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

class Process:
	def __init__(self, stream):
		self.streams = []
		self.streams.append(stream)

	def addStream(self, stream):
		self.streams.append(stream)

def reformatIP(IP):
	k = IP.rfind(".")
	result = IP[:k] + ':' + IP[k+1:]
	return result

def extractSize(stream):
	y=0
	try:
		y = stream.size * 8		# Bytes to bits
	except Exception as e:
		y=0
	return y

def plotHighestHistory(streamHistory):
	highestHistory = {}
	for time, streamDict in streamHistory.items():
		highest = 0
		stream = {}
		for k, v in streamDict.items():
			if v.size > highest:
				highest = v.size
				stream = v
		highestHistory[time] = stream
	x = highestHistory.keys()
	y = list(extractSize(stream) / 10000000 for stream in highestHistory.values())
	plt.xlabel('time (s)')
	plt.ylabel('bitstream (Mbps)')
	plt.grid(True)
	plt.plot(x, y)
	plt.savefig('plot.png')
	plt.close()

def plotAllHistory(streamHistory):
	processDict = {}

def plotAllProcesses(processHistory):
	processes = {}
	for time, processDict in processHistory.items():
		for name, process in processDict.items():
			if not name in processes:
				processes[name] = []
			processes[name].append({
				'time': time,
				'up': next((stream.size for stream in process.streams if stream.direction == 'up'), 0),
				'down': next((stream.size for stream in process.streams if stream.direction == 'down'), 0)
			})
	# print(processes)
	plt.xlabel('time (s)')
	plt.ylabel('bitstream (Mbps)')
	plt.grid(True)
	legend = []
	for process in processes.items():
		print(process[0])
		legend.append(process[0])
		x = list(history['time'] for history in process[1])
		y = list((history['down'] * 8) / 10000000 for history in process[1])
		plt.plot(x, y)
	plt.legend(legend)
	plt.savefig('plot1_down.png')
	plt.close()

	plt.xlabel('time (s)')
	plt.ylabel('bitstream (kbps)')
	legend = []
	for process in processes.items():
		print(process[0])
		legend.append(process[0])
		x = list(history['time'] for history in process[1])
		y = list((history['up'] * 8) / 10000 for history in process[1])
		plt.plot(x, y)
	plt.legend(legend)
	plt.savefig('plot1_up.png')
	plt.close()

i = 1
streamHistory = {}
processHistory = {}

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
    		print(1, i, j, e)
    		continue
    netstatContents = netstat.read().split()
    processDict = {}
    for ip, stream in streamDict.items():
    	localIP = stream.destination
    	if stream.direction == 'up':
    		localIP = stream.source
    	try:
    		process = netstatContents[(netstatContents.index(localIP) + 3)]
    	except:
    		try:
    			port = localIP.split(':')[1]
    			index = [ i for i, word in enumerate(netstatContents) if word.endswith(port) ]
    			process = netstatContents[index[0] + 3]
    		except Exception as e:
    			print(2, i, j, e)
    			continue
    	if process in processDict:
    		processDict[process].addStream(stream)
    	else:
    		processDict[process] = Process(stream)
    	stream.setProcess(process)
    	streamString = str(stream)
    	streams.write(streamString+"\n")
    streamHistory[i*10] = streamDict
    processHistory[i*10] = processDict
    netstat.close()
    tcpdump.close()
    i+=1

plotHighestHistory(streamHistory)
plotAllProcesses(processHistory)

plotAllHistory(streamHistory)