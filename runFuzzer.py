#
# Fuzzer template (FTP-Server)
# Use with Dynamips GDB server patch
# and GDB > 7.2, with --target=powerpc-elf
#
# Load from inside GDB with:
#	(gdb) source runFuzzer.py
#
# Sebastian Muniz - Alfredo Ortega
# smuniz@groundoworkstech.com - aortega@groundworkstech.com
# Groundworks Technologies
# http://www.groundworkstech.com
#

import os,time,socket
from subprocess import Popen,PIPE
from multiprocessing import Process

# Customize here
GDBPORT=12345
FTPSERVER="10.100.100.200"
FTPUSER="anonymous"
FTPPASS="a@a.com"
DYNAMIPS="../../dynamips-0.2.8-RC2/dynamips"
IOSIMAGE="../C1700-EN.BIN"


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


def log(str):
	a=open("fuzz.log","ab")
	a.write(str)
	a.close()
	print bcolors.OKBLUE+str+bcolors.ENDC

def enableTunTap():
	print bcolors.WARNING+"Configuring tun/tap interface..."+bcolors.ENDC
	#os.system("./networking.sh")
	time.sleep(1)

def launchDynamips():
	print bcolors.WARNING+"Launching Dynamips..."+bcolors.ENDC
	os.system("rm *_lock") # remove possible stale lock file
	opcommand = Popen([DYNAMIPS,"-Z",str(GDBPORT), "-j", "-P","1700","-s","0:0:tap:tap0",IOSIMAGE], stdin=PIPE)
	time.sleep(1)
	return opcommand

def debugDynamips():
	gdb.execute("target remote : %d" % GDBPORT)
	time.sleep(1)
	gdb.execute("c")
	log (gdb.execute("i r",to_string=True))
	log (gdb.execute("bt",to_string=True))
	log (gdb.execute("x/10i $pc-8",to_string=True))
	gdb.execute("detach")
	
def enableFTP():
	print bcolors.WARNING+"Enabling FTP..."+bcolors.ENDC
	opcommand.stdin.write("\r\n")
	opcommand.stdin.write("\r\n")
	opcommand.stdin.write("\r\n")
	time.sleep(0.1)
	opcommand.stdin.write("en\r\n")
	time.sleep(0.1)
	opcommand.stdin.write("configure terminal\r\n")
	time.sleep(0.1)
	opcommand.stdin.write("ftp-server enable\r\n")
	time.sleep(0.1)
	return opcommand

	#Connect to FTP and login with anonymous user
def loginFtp():
	print bcolors.WARNING+"Connecting to FTP..."+bcolors.ENDC
	s=socket.socket()
	s.settimeout(5)
	s.connect((FTPSERVER,21))
	print s.recv(100)
	s.send("USER %s\r\n" % FTPUSER)
	print s.recv(100)
	s.send("PASS %s\r\n" % FTPPASS)
	print s.recv(100)
	return s

	# Get commands from HELP
def getFtpCommands():
	s=loginFtp()
	s.send("HELP\r\n")
	time.sleep(0.5)
	helpstr=s.recv(1000)
	s.close()
	helpstr=helpstr.split("\r\n")[1:-2]
	cmds=[]
	for line in helpstr:
        	cmds = cmds + line.split("   ")[1:]
	#cmds=["mkd"]
	return cmds


	# Send RAW FTP command
def sendFTPCommand(command):
	log("---- Fuzzing %s -----\n" % command)
	s=loginFtp()
	s.send("SYST\r\n")
	s.recv(10)
	s.send(command)
	result=s.recv(1000)
	s.send("QUIT\r\n")
	s.recv(100)
	s.close()
	return result
	
def waitt(sec):
	for i in range(sec):
		time.sleep(1)
		print bcolors.OKGREEN+("%d" % i)+bcolors.ENDC

#************************** main ***************************
#init fuzzer
gdb.execute("set pagination off")
#clean log
os.system("rm fuzz.log") 
#configure network interface
enableTunTap()
#launch Dynamips process
opcommand=launchDynamips()
#attach in a new process
p = Process(target=debugDynamips,args=())
p.start()
waitt(70) # booting...
#Enable FTP server in config
enableFTP()
#List valid FTP commands
waitt(3)
cmds=getFtpCommands()
print bcolors.WARNING+"Valid commands:"
print repr(cmds)+bcolors.ENDC
#fuzz!
for cmd in cmds:
	try:
		print bcolors.WARNING+("Fuzzing command '%s'..." % cmd.strip())+bcolors.ENDC
		time.sleep(2)
		sendFTPCommand("%s %s" % (cmd.strip().upper(),"A"*100))
	except: #probably crashed! restarting...
		print bcolors.FAIL+"************ CRASH! ****************"+bcolors.ENDC
		print bcolors.FAIL+"***********************************"+bcolors.ENDC
		print bcolors.FAIL+"************ REBOOT ***************"+bcolors.ENDC
		time.sleep(3)
		opcommand.terminate()
		opcommand=launchDynamips()
		p = Process(target=debugDynamips,args=())
		p.start()
		waitt(70) # booting...
		enableFTP()
		waitt(3)
print bcolors.FAIL+"************ FINISHED ****************"+bcolors.ENDC
p.terminate()
opcommand.kill() 
