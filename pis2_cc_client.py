import os, sys
import socket
import shutil
import subprocess

########################################################################################################
# CONFIG SECTION
SERVER_IP = '192.168.0.2'
SERVER_PORT = 9999
EMULATOR_RUN = True
EMULATOR_PATH = 'C:\\PS2\\Emulator\\PCSX2 1.4.0\\pcsx2.exe'
########################################################################################################

if len(sys.argv) == 3:

	print('\n***************************************************************************\nPiS2 Cloud Compiler v0.1 by Logi26\n')
	selectedFolder = sys.argv[1]

	if os.path.isdir(selectedFolder):
		zipPath = os.path.dirname(os.path.realpath(sys.argv[0])) + '\\zipped'
		shutil.make_archive(zipPath, 'zip', selectedFolder)
		zipPath += '.zip'

		try:
			serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			serverSocket.connect((SERVER_IP, SERVER_PORT))
			serverSocket.send(str(os.path.getsize(zipPath)))
			
			if 'RECIEVED' in serverSocket.recv(8):
				elfName = str(sys.argv[2])
				if not '.elf' in elfName: elfName += '.elf'
				serverSocket.send(elfName)
				
				if 'RECIEVED' in serverSocket.recv(8):
					zipFile = open(zipPath,'rb')
					chunk = zipFile.read(1024)
					while (chunk):
						serverSocket.send(chunk)
						chunk = zipFile.read(1024)
					zipFile.close()
					print('\nData uploaded.\nPlease wait for the server to compile and return your ELF file.')
				else:
					print('\nThe server is not responding at the moment!')	

				os.remove(zipPath)
				elfCompiled = serverSocket.recv(1)
				serverSocket.send('RECIEVED')
				fileSize = serverSocket.recv(50)
				print('Recieving file of %s bits...' % fileSize)
				buffer = ''
				serverSocket.send('RECIEVED')

				while len(buffer) < int(fileSize): buffer += serverSocket.recv(1024)
	
				if elfCompiled == '1': elfPath = os.path.dirname(os.path.realpath(sys.argv[0])) + '\\' + elfName
				else: elfPath = os.path.dirname(os.path.realpath(sys.argv[0])) + '\\make_log.txt'
				
				elfFile = open(elfPath,'wb')
				elfFile.write(buffer)
				elfFile.close()
				
				if EMULATOR_RUN and elfCompiled == '1':
					cmd = [EMULATOR_PATH, '--nogui', '--console', '--elf=' + elfPath]
					process = subprocess.Popen(cmd)		
		except:
			os.remove(zipPath)
			print('\nUnable to establish a connection with the server!')
	else:
		print('\nThe path that you have entered does not point to a valid directory!')	
	print('***************************************************************************\n')	
else:
	print('\n***************************************************************************\n'
		+ '  Script requires the directory path and output elf name as a parameters:\n'
		+ '  python pis2_cc_client.py C:\\ps2_homebrew\\open-ps2-loader opl.elf\n'
		+ '***************************************************************************\n')
