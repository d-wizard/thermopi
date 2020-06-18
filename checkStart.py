import sys
import os
import time

BIN_DIR = os.path.dirname(os.path.realpath(__file__))

SCRIPT_NAME = 'temperatureControlSwitch.py'
SCRIPT_PATH    = os.path.join(BIN_DIR, SCRIPT_NAME)
ERROR_LOG_PATH = os.path.join(BIN_DIR, 'temperatureControlSwitch.stderr')

START_CMD = 'python ' + SCRIPT_PATH + ' 2>> ' + ERROR_LOG_PATH + ' &'

# Add path to the python file needed to run this script (e.g. getAllProcesses)
sys.path.append(os.path.join(BIN_DIR, '..', 'PythonLibraries'))
from getAllProcesses import getProcInfo

procInfo = getProcInfo('python')

running = False
for p in procInfo:
   if SCRIPT_NAME in p.cmds:
      running = True
   else:
      for cmd in p.cmds:
         if SCRIPT_NAME in cmd:
            running = True

if not running:
   os.system(START_CMD)
