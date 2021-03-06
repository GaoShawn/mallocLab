from socket import *
import struct
import thread
import os

ADDR = ('211.87.235.74',8000)

bestResult = 0

BUFSIZE = 1024
FILEINFO_SIZE=struct.calcsize('128s32sI8s')
recvSock = socket(AF_INET,SOCK_STREAM)
recvSock.bind(ADDR)
recvSock.listen(True)

def test(name,passwd):
	sourceFile=open("passwd.txt","r")
	while True:
		line = sourceFile.readline()
		if not line:
			break
		dataArray = line.split()
		if(dataArray[0]==name and dataArray[1]==passwd):
			return 1
	return 0

def sendData(conn,filename):
	global bestResult
	fp = open(filename,'rb')
	fhead=struct.pack('128s11I',filename,0,0,0,0,0,0,0,0,os.stat(filename).st_size,0,0)
	conn.send(fhead)
	while 1:
		filedata=fp.readline()
		if not filedata: break
		conn.send(filedata)
		dataArray = filedata.split(':')
		if(len(dataArray)>=1):
			if(dataArray[0] == 'perfidx' and int(dataArray[1])>bestResult):
				bestResult=dataArray[1]
	conn.send(str(len(str(bestResult))))
	conn.send(bestResult)
	print "\nsend completed..."

def readDate(conn,addr):
	len_name = conn.recv(1)
	name=conn.recv(int(len_name))
	try:
		len_name = conn.recv(2)
		passwd=conn.recv(int(len_name))
	except Exception,ex:
   		print Exception,":",ex
   		sendData(conn,"error.txt")
		conn.close()
		return
	print name,passwd
	isvalid = test(name,passwd)
	if(isvalid==0):
		sendData(conn,"error.txt")
		conn.close()
		return
		
	fhead = conn.recv(FILEINFO_SIZE)
	
	filename,temp1,filesize,temp2=struct.unpack('128s32sI8s',fhead)

	print filename,filesize

	filename = "source/"+name+"_mm.c"    #recieved file
	fp = open(filename,'wb')
	restsize = filesize

	while 1:    #read file data 
		if restsize > BUFSIZE:
		    filedata = conn.recv(BUFSIZE)
		else:
		    filedata = conn.recv(restsize)

		if not filedata: break
		fp.write(filedata)
		restsize = restsize-len(filedata)
		if restsize == 0:
			break
	print "recieve completed ..."
	fp.close()
	import subprocess
	var = "/usr/bin/perl"
	subprocess.call(["perl", "grade-malloclab.pl",'-f', filename,var])
	sendData(conn,"res/"+name+"_mm.c_res.txt")
	
	conn.close()

while(True):   # waiting to connect
	print "waiting....."
	conn,addr = recvSock.accept()
	thread.start_new_thread(readDate,(conn,addr))
	
	#print "close..."

recvSock.close()
