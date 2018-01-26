import os, sys
import socket
import threading
import subprocess
import zipfile
import shutil

########################################################################################################
# CONFIG SECTION
TCP_IP = '192.168.0.2'
TCP_PORT = 9999
########################################################################################################

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((TCP_IP, TCP_PORT))
server.listen(2)
print '\nPiS2 Cloud Compiler - listening on {}:{}'.format(TCP_IP, TCP_PORT)

def sendFile(compiled, filePath):
	clientSocket.send(compiled)
	if 'RECIEVED' in clientSocket.recv(8):
		clientSocket.send(str(os.path.getsize(filePath)))
		if 'RECIEVED' in clientSocket.recv(8):
			theFile = open(filePath,'rb')
			chunk = theFile.read(1024)
			while (chunk):
				clientSocket.send(chunk)
				chunk = theFile.read(1024)
			theFile.close()
				
def handleConnection(clientSocket):
        fileSize = clientSocket.recv(50)
        clientSocket.send('RECIEVED')

        elfName = clientSocket.recv(256)
        buffer = ''
        clientSocket.send('RECIEVED')

        while len(buffer) < int(fileSize):
                buffer += clientSocket.recv(1024)

        zipPath = os.path.dirname(os.path.realpath(sys.argv[0])) + '/pi_compile.zip'
        zipOutputFile = open(zipPath,'wb')
        zipOutputFile.write(buffer)
        zipOutputFile.close()

        zip_ref = zipfile.ZipFile(zipPath, 'r')
        zip_ref.extractall(os.path.dirname(os.path.realpath(sys.argv[0])) + '/pi_compile')
        zip_ref.close()

        os.remove(zipPath)
        os.chdir(os.getcwd() + '/pi_compile')
        makeLogPath = os.getcwd() + '/make_log.txt'
        makeLogFile = open(makeLogPath, 'w+')

        proc = subprocess.Popen(["make"], stdout=makeLogFile)
        stdout, stderr = proc.communicate()

        makeLogFile.close()
        elfPath = os.getcwd() + '/' + elfName

        if os.path.isfile(elfPath): sendFile('1', elfPath)
	else: sendFile('0', makeLogPath)

        os.chdir(os.getcwd() + '/../')
        shutil.rmtree(os.getcwd() + '/pi_compile')
	print 'Closing connection with client {}:{}'.format(address[0], address[1])
        clientSocket.close()

while True:
        clientSocket, address = server.accept()
        print '\nAccepted connection from {}:{}'.format(address[0], address[1])
        client_handler = threading.Thread(target = handleConnection, args = (clientSocket,))
        client_handler.start()
