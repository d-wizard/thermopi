import os
import argparse
import json
import time
from datetime import datetime

import ipc


ipcSocketPath = os.path.split(os.path.realpath(__file__))[0] + os.sep + 'ipcSocket'


################################################################################
# Logging
################################################################################
def appendFile(path, fileText):
   try:
      fileId = open(path, 'a')
      fileId.write(fileText)
      fileId.close()
   except:
      pass

def logToFile(printMsg, unimportantMsg = False):
   logNewLine = '\n'
   shortTimeFormat = "%H:%M %m/%d"   # 24 hour value
   #shortTimeFormat = "%I:%M%p %m/%d" # 12 hour value with AM/PM
   shortTimeStr = "{}".format(time.strftime(shortTimeFormat))
   longTimeStr  = str(datetime.now())

   logMsg = '[' + longTimeStr + "] " + printMsg
   
   logPath = os.path.splitext(os.path.realpath(__file__))[0] + '.log'
   appendFile(logPath, logMsg + logNewLine)


################################################################################
# IPC Client For New Json Settings
################################################################################
class Event(ipc.Message):
    def __init__(self, event_type, **properties):
        self.type = event_type
        self.properties = properties

    def _get_args(self):
        return [self.type], self.properties

class Response(ipc.Message):
    def __init__(self, text):
        self.text = text

    def _get_args(self):
        return [self.text], {}

def setGet(newSettings = None): # Returns dictionary
    global ipcSocketPath

    if newSettings == None:
        kwargs = {'query':''} # This can really be anything other than 'json'
    else:
        kwargs = {'json':json.dumps(newSettings)}

    user_input = [{'class': 'Event', 'args': ['newSettings'], 'kwargs': kwargs}]
    objects = ipc.Message.deserialize(user_input)

    try:
        with ipc.Client(ipcSocketPath) as client:
            response = client.send(objects)
    except Exception as e:
        logToFile("failed to send: " + str(e))
        pass

    try:
        responseDict = json.loads(response[0].text)
    except Exception as e:
        logToFile("failed to load json: " + str(e))
        responseDict = None
        pass

    return responseDict


# Json Keywords
SettingsKeyWords = [
    "TimeOfDayToStart",                  
    "TimeOfDayToStop",                   
    "SwitchTemperature",                        
    "SwitchComfortRange",                
    "SwitchHeatCool",                
    "SmartPlugIpAddr",                   
    "MinTimeBetweenChangingSwitchState", 
    "MinTimeBetweenRetryingSwitchChange",
    "TimeBetweenTempCheck",              
    "InvalidTempLow",                    
    "InvalidTempHigh",                   
    "SwitchStateAfterTimeOfDayStop",
    "DeviceName",
    "DeviceColor"
]

StatusKeyWords = [
    "Temp",
    "SwitchState"
]


################################################################################
# Program Start
################################################################################
#logToFile("start")
#logToFile(os.getcwd())

# Config argparse
parser = argparse.ArgumentParser()

for keyword in SettingsKeyWords:
    cmd = '--' + keyword
    parser.add_argument(cmd, type=str, action="store", dest=keyword, help=keyword)
args = parser.parse_args()


# Update Dict with values from command line.
settingsDict = dict()
needToChange = False
for arg in vars(args):
    argVal = getattr(args, arg)
    if argVal != None:
        needToChange = True
        settingsDict[arg] = str(argVal)

# Apply the changes.
if needToChange:
    responseDict = setGet(settingsDict)
else:
    responseDict = setGet()

# Print string with all the new values.
printStr = ''

for keyword in SettingsKeyWords:
    try:
        printStr += (responseDict["settings"][keyword] + "|")
    except:
        printStr += " |"
for keyword in StatusKeyWords:
    try:
        printStr += (responseDict["status"][keyword] + "|")
    except:
        printStr += " |"

print(printStr)
