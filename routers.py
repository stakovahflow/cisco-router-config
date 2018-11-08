#!/usr/bin/env python
#####################################################
# IMPORTS:
try:
	import sys,time,datetime,os,re,csv,base64,pexpect
except:
	print('unable to import one or more of your libraries')
	exit(0)

#####################################################
# DEBUG-ish:
v = True

def errorOut(CMD):
	print("A really significant problem occurred and %s is exiting." % (CMD))
	exit(0)

CMD=sys.argv[0]

if (len(sys.argv) == 3):
	if (v == True):
		print("Correct number of arguments provided.")
else:
	if (v == True):
		print("Incorrect number of arguments.")
	errorOut(CMD)
exit(0)

try:
	routerlist = sys.argv[1]
	if (v == True):
		print("Router list: %s" % (routerlist))
except:
	print('Unable to set router list to "%s"' % (routerlist))
	errorOut(CMD)

try:
	passlist = sys.argv[2]
	if (v == True):
		print("Password lists: %s" % (passlist))
except:
	print('Unable to set password list to "%s"' % (passlist))
	errorOut(CMD)

# Set Pexpect Timeout:
TimeOut = 15

# Base backup directory:
BKPCFGDIR = '/cisco/backup'

#####################################################
#####################################################
#####################################################
# Here's our main function:

def runner(SName, SAddr):
	#####################################################
	# Set Cisco usernames:
	# (UserName is the TACACS+ user)
	# (UserName2 is the local device user)
	i = 0
	try:
		if v == True:
			print('attempting to open passfile: %s' % (passlist))
		with open(passlist,'r') as passfile:
			for i, password in enumerate(csv.reader(passfile)):
				if (i == 0):
					UserName1=password[0]
					if v == True:
						print("UserName1 set: %s" % (UserName1))
					PassWord1 = base64.b64decode(password[1])
					if v == True:
						print("PassWord1 set")
				elif (i == 1):
					UserName2=password[0]
					if v == True:
						print("UserName2 set: %s" % (UserName2))
					PassWord2 = base64.b64decode(password[1])
					if v == True:
						print("PassWord2 set")
				else:
					break
	except:
		print("Unable to obtain username/passwords from file: %s" % (passlist))
		print("Make sure that your passwords are base64 encoded:")
		print(">>> import base64")
		print(">>> base64.b64encode('password')")
		print("'cGFzc3dvcmQ='")
		print("To verify the password: ")
		print(">>> base64.b64decode('cGFzc3dvcmQ=')")
		print("'password'")
		errorOut(CMD)
	passfile.close()
	#####################################################
	# Setup our loop for the "--More--"
	LOOP = True
	MORE = '--More--'
	#####################################################
	# CONFIGURATION and TEMP FILE DIRECTORIES:
	BKPCFGTMPDIR = ('%s/temp' % (BKPCFGDIR))
	#####################################################
	# CONFIGURATION and TEMP FILES:
	CFGTMPFILENAME = '%s/%s.tmp' % (BKPCFGTMPDIR, SName)
	CFGFILENAME = ('%s/%s.cfg' % (BKPCFGDIR, SName))
	CFGTMPFILENAME1 = ("%s1" % (CFGTMPFILENAME))
	CFGTMPFILENAME2 = ("%s2" % (CFGFILENAME))
	#####################################################
	# OUTPUT to /dev/null:
	fout = open('/dev/null','w')
	#####################################################
	# Set our configuration filename:
	try:
		CFGFILE = open(CFGTMPFILENAME,'w')
		print('Configuration file to save: %s' % (CFGTMPFILENAME))
	except:
		print('Destination configuration file or directory unwritable: %s/%s.cfg' % (BKPCFGTMPDIR, SName))
	#####################################################
	# LET'S ROLL THAT BEAUTIFUL BEAN FOOTAGE!:
	print("Attempting to establish connection to %s (%s)" % (SName,SAddr))
	try:
		if (v == True):
			print('Primary credentials.')
		UserName = UserName1
		PassWord = PassWord1
		print("%s" % (UserName))
		child = pexpect.spawn('/usr/bin/ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -l %s %s' % (UserName,SAddr))
		child.logfile = fout
		if (v == True):
			print(child.before)
		time.sleep(3)
		child.expect ('Password:')
		if (v == True):
			print(child.before)
		child.sendline (PassWord)
		time.sleep(3)
		child.expect ('>')
		if (v == True):
			print(child.before)
	except:
		if (v == True):
			print('Alternate credentials.')
		UserName = UserName2
		PassWord = PassWord2
		print("%s" % (UserName))
		child = pexpect.spawn('/usr/bin/ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -l %s %s' % (UserName,SAddr))
		child.logfile = fout
		if (v == True):
			print(child.before)
		time.sleep(3)
		child.expect ('Password:')
		if (v == True):
			print(child.before)
		child.sendline (PassWord)
		child.expect ('>')
		if (v == True):
			print(child.before)
	try:
		try:
			if (v == True):
				print("Received the > prompt")
			child.sendline ('en')
		except:
			if (v == True):
				print("Didn't receive the > prompt")
			time.sleep(1)
			child.sendline ('en')
		try:
			child.expect ('Password:')
			child.sendline (PassWord)
			if (v == True):
				print("Received the Password prompt")
		except:
			time.sleep(1)
			child.sendline (PassWord)
			if (v == True):
				print("Didn't receive the Password prompt")
		try:
			child.expect ('#')
			if (v == True):
				print("Received the # prompt")
		except:
			time.sleep(1)
			child.sendline (PassWord)
			if (v == True):
				print("Didn't receive the # prompt")
		# Set logging to console:
		child.logfile = sys.stdout
		if (v == True):
			print("Logging to sys.stdout")
		# SHOW hostname:
		child.sendline ('show run | in hostname')
		child.expect ('#')
		
		# SHOW version:
		child.sendline ('show ver | in flash')
		child.expect ('#')
		
		# SHOW inventory (SN):
		child.sendline ('show inventory | in SN')
		while LOOP == True:
			try:
				child.expect(MORE)
				child.send(' ')
				LOOP = True
			except:
				LOOP = False
		# SHOW running-config:
		if (v == True):
			print("Reset LOOP")
		LOOP = True
		child.expect ('#')
		child.sendline('show running-config')
		try:
			if (v == True):
				print("let's try this via show run and logging to file: %s" % (CFGTMPFILENAME))
			child.logfile = CFGFILE
			while LOOP == True:
				try:
					child.expect(MORE)
					child.send(' ')
					sys.stdout.write(".")
					sys.stdout.flush()
					LOOP = True
				except:
					LOOP = False
			if (v == True):
				print("\nreset output to sys.stdout\n")
			else:
				print("\n")
		except:
			print('boo, dirty tftp and ssh connectivity!')
		child.logfile = sys.stdout
		time.sleep(1)
		child.sendline('')
		child.expect('#')
		child.sendline ('exit')
		child.close()
		CFGFILE.close()
	except:
		print("Connection to %s failed." % (SAddr))
	try:
		spaces=15
		time.sleep(2)
		if (v == True):
			print('Copying config')
		os.system('cp %s %s' % (CFGTMPFILENAME, CFGTMPFILENAME1))
		if (v == True):
			print('Stripping "show running-config"')
		os.system("sed -i 's/show\ running-config.*//g' %s " % (CFGTMPFILENAME1))
		if (v == True):
			print('Stripping "Building configuration"')
		os.system("sed -i 's/Building\ configuration.*//g' %s " % (CFGTMPFILENAME1))
		if (v == True):
			print('Stripping "Current configuration"')
		os.system("sed -i 's/Current\ configuration/!\ Current\ configuration/g' %s " % (CFGTMPFILENAME1))
		if (v == True):
			print('Stripping empty lines')
		os.system("grep -v '^$\|^!$' %s > %s" % (CFGTMPFILENAME1,CFGTMPFILENAME2))
		if (v == True):
			print('Renaming %s to %s:' % (CFGTMPFILENAME2,CFGTMPFILENAME1))
		os.system("mv %s %s" % (CFGTMPFILENAME2,CFGTMPFILENAME1))
		if (v == True):
			print('Stripping "--More"')
		os.system("tr -d '\b\r' < %s | sed 's/--More--//g' > %s " % (CFGTMPFILENAME1,CFGTMPFILENAME2))
		if (v == True):
			print('stripping spaces from the beginning of lines')
		while spaces >= 0:
			os.system("sed -i 's/^\ //g' %s" % (CFGTMPFILENAME2))
			spaces = spaces - 1
		try:
			if (v == True):
				print('Attempting to open files for reading and writing')
			INFILE=open(CFGTMPFILENAME2,'r')
			OUTFILE=open(CFGFILENAME,'w')
			if (v == True):
				print('Attempting to read file: %s' % (CFGTMPFILENAME2))
			INPUT = INFILE.readlines()
			if (v == True):
				print('Attempting to strip last line from config')
			INPUT = INPUT[:-1]
			OUTFILE.writelines(INPUT)
		except:
			if (v == True):
				print('Attempting to close open files.')
			print('this thing is broken')
			CFGTMPFILENAME2.close()
			CFGFILENAME.close()
		if (v == True):
			print('Attempting to list config file and delete temp files.')
		if (v == True):
			print('Attempting to remove %s' % (CFGTMPFILENAME2))
		os.system("rm -rf %s" % (CFGTMPFILENAME2))
		if (v == True):
			print('Attempting to remove %s' % (CFGTMPFILENAME1))
		os.system("rm -rf %s" % (CFGTMPFILENAME1))
		if (v == True):
			print('Attempting to remove %s' % (CFGTMPFILENAME))
		os.system("rm -rf %s" % (CFGTMPFILENAME))
		if (v == True):
			print('Attempting to list %s' % (CFGFILENAME))
		os.system('ls -lh %s' % (CFGFILENAME))
	except:
		print('Something happened')
	return 0

#####################################################
# Open our CSV and kick it!
#####################################################
with open(routerlist,'r') as routerfile:
	routers = csv.reader(routerfile)
	for router in routers:
		SName=router[0]
		SAddr=router[1]
		if (v == True):
			print("%s - %s" % (SName,SAddr))
		runner(SName,SAddr)

print("Complete")
