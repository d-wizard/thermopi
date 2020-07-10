import os
import time
import math
import sys
import json
import copy
from datetime import datetime
from threading import Thread, Lock

import temperatureSensorLib
import smartPlugLib
import ipc
from getTempChartArray import updateTemperatureLogFile


################################################################################
# Setting Specified Via The .json File
################################################################################

class tempCtrlSwitchSettings(object):
   def __init__(self):
      self.MIN_TIME_BETWEEN_CHANGING_SWITCH_STATE = None # in seconds
      self.MIN_TIME_BETWEEN_RETRYING_SWITCH_CHANGE= None # in seconds

      self.TIME_BETWEEN_TEMPERATURE_CHECK = None # in seconds

      self.SWITCH_ON_TEMPERATURE  = None # in degrees Fahrenheit 
      self.SWITCH_OFF_TEMPERATURE = None # in degrees Fahrenheit

      self.SMART_PLUG_IP_ADDR = None

      self.TIME_OF_DAY_TO_START = None
      self.TIME_OF_DAY_TO_STOP  =  None
      self.SWITCH_STATE_AFTER_TIME_OF_DAY_STOP = False # False for off, True for on, None for no change

      self.TEMPERATURE_AVERAGE_TIME_AMOUNT = None
      self.INVALID_TEMPERATURE_LOW  = None # in degrees Fahrenheit
      self.INVALID_TEMPERATURE_HIGH = None # in degrees Fahrenheit

      self.DEVICE_NAME = None
      self.DEVICE_COLOR = None

   def __eq__(self, obj):
      return isinstance(obj, tempCtrlSwitchSettings) and \
      obj.MIN_TIME_BETWEEN_CHANGING_SWITCH_STATE == self.MIN_TIME_BETWEEN_CHANGING_SWITCH_STATE and \
      obj.MIN_TIME_BETWEEN_RETRYING_SWITCH_CHANGE == self.MIN_TIME_BETWEEN_RETRYING_SWITCH_CHANGE and \
      obj.TIME_BETWEEN_TEMPERATURE_CHECK == self.TIME_BETWEEN_TEMPERATURE_CHECK and \
      obj.SWITCH_ON_TEMPERATURE == self.SWITCH_ON_TEMPERATURE and \
      obj.SWITCH_OFF_TEMPERATURE == self.SWITCH_OFF_TEMPERATURE and \
      obj.SMART_PLUG_IP_ADDR == self.SMART_PLUG_IP_ADDR and \
      obj.TIME_OF_DAY_TO_START == self.TIME_OF_DAY_TO_START and \
      obj.TIME_OF_DAY_TO_STOP == self.TIME_OF_DAY_TO_STOP and \
      obj.SWITCH_STATE_AFTER_TIME_OF_DAY_STOP == self.SWITCH_STATE_AFTER_TIME_OF_DAY_STOP and \
      obj.TEMPERATURE_AVERAGE_TIME_AMOUNT == self.TEMPERATURE_AVERAGE_TIME_AMOUNT and \
      obj.INVALID_TEMPERATURE_LOW == self.INVALID_TEMPERATURE_LOW and \
      obj.INVALID_TEMPERATURE_HIGH == self.INVALID_TEMPERATURE_HIGH and \
      obj.DEVICE_NAME == self.DEVICE_NAME and \
      obj.DEVICE_COLOR == self.DEVICE_COLOR
   def __ne__(self, obj):
      result = self.__eq__(obj)
      if result is NotImplemented:
         return result
      return not result


currentTempCtrlSettings = tempCtrlSwitchSettings()
currentTempCtrlDict = dict()
settingsMutex = Lock()

################################################################################
# Constant Variables
################################################################################
THIS_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
THIS_SCRIPT_FILENAME_NO_EXT = os.path.splitext(os.path.realpath(__file__))[0] 
JSON_PATH = THIS_SCRIPT_FILENAME_NO_EXT + '.json'
IPC_SOCKET_PATH = os.path.join(THIS_SCRIPT_DIR, 'ipcSocket')
WEB_LOG_PATH = os.path.join(THIS_SCRIPT_DIR, 'web', 'tempCtrlSwitch.log')


################################################################################
# Global Variables
################################################################################
lastSuccessfulSwitchChangeTime = -1000000 # Initialize to a time way in the past to ensure
lastFailedSwitchChangeTime     = -1000000 # the switch can be set right away at boot time.

nextTemperatureCheckTime = 0

activeDuringTimeOfDayToControlSwitch = False

temperatureStoreValuesForAverage = []

lastTemperatureValue   = None
lastTemperatureAverage = None

lastTemperatureLogTime = 0

currentSwitchState = None # False for off, True for on, None unknown

logNewLine = '\n'
logMaxLogLines_short = 5000
logLineToLeaveAfterTrim_short = 3000
logMaxLogLines_long = 50000
logLineToLeaveAfterTrim_long = 30000


################################################################################
# Enumerated Values
################################################################################
SWITCH_STATE_OFF       = "Off"
SWITCH_STATE_ON        = "On"
SWITCH_STATE_NO_CHANGE = "No Change"

CHANGE_SWITCH_RESULT_SUCCESS_NO_CHANGE_NEEDED     = "Success - No Change Needed"
CHANGE_SWITCH_RESULT_SUCCESS_SWITCH_STATE_CHANGED = "Success - Switch State Changed"
CHANGE_SWITCH_RESULT_FAILED                       = "Failed"


################################################################################
# Generic Helper Functions
################################################################################
def readWholeFile(path):
   retVal = ""
   try:
      fileId = open(path, 'r')
      retVal = fileId.read()
      fileId.close()
   except:
      pass
   return retVal
   
def writeWholeFile(path, fileText):
   try:
      fileId = open(path, 'w')
      fileId.write(fileText)
      fileId.close()
   except:
      pass

def appendFile(path, fileText):
   try:
      fileId = open(path, 'a')
      fileId.write(fileText)
      fileId.close()
   except:
      pass

def limitLogSize(logFilePath, trimFromTop, logMaxLogLines, logLineToLeaveAfterTrim):
   logFile = readWholeFile(logFilePath)
   lineCount = logFile.count(logNewLine)

   if lineCount > logMaxLogLines:
      if trimFromTop:
         logFile = logNewLine.join(logFile.split(logNewLine)[-logLineToLeaveAfterTrim:])
      else:
         logFile = logNewLine.join(logFile.split(logNewLine)[:logLineToLeaveAfterTrim])
      writeWholeFile(logFilePath, logFile)


def logMsg(printMsg, unimportantMsg = False):
   shortTimeFormat = "%H:%M %m/%d"   # 24 hour value
   #shortTimeFormat = "%I:%M%p %m/%d" # 12 hour value with AM/PM
   shortTimeStr = "{}".format(time.strftime(shortTimeFormat))
   longTimeStr  = str(datetime.now())

   logMsg = '[' + longTimeStr + "] " + printMsg
   print(logMsg)
   
   logPath = os.path.splitext(os.path.realpath(__file__))[0] + '.log'
   appendFile(logPath, logMsg + logNewLine)
   limitLogSize(logPath, True, logMaxLogLines_long, logLineToLeaveAfterTrim_long)

   try:
      if not unimportantMsg:
         temperatureStr = str(lastTemperatureValue)
         if lastTemperatureValue != None:
            temperatureStr = "{:.1f}".format(lastTemperatureValue)
         
         logMsg = temperatureStr + " " + shortTimeStr + "-" + printMsg
         writeWholeFile(WEB_LOG_PATH, logMsg + logNewLine + readWholeFile(WEB_LOG_PATH))
         limitLogSize(WEB_LOG_PATH, False, logMaxLogLines_short, logLineToLeaveAfterTrim_short)
   except:
      print "Failed to log to web. - " + WEB_LOG_PATH
      
      

def getCurrentTime():
   uptime_seconds = None

   try:
      with open('/proc/uptime', 'r') as f:
          uptime_seconds = float(f.readline().split()[0])
   except:
      logMsg("Failed to get current time")

   return uptime_seconds



################################################################################
# JSON Functions
################################################################################
def strToTimeInt(inStr):
   try:
      iniTimeStr = inStr.lower()

      hour = 0
      minute = 0
      isPm = None

      # Determine AM / PM
      if iniTimeStr[-2:] == "pm":
         isPm = True
      elif iniTimeStr[-2:] == "am":
         isPm = False
      if isPm != None:
         iniTimeStr = iniTimeStr[:-2]
      
      if ':' in iniTimeStr:
         hour = int(iniTimeStr.split(':')[0])
         minute = int(iniTimeStr.split(':')[1])
      else:
         totalTime = int(iniTimeStr)
         if totalTime >= 100:
            hour = totalTime / 100
            minute = totalTime % 100
         elif totalTime < 24:
            hour = totalTime
            minute = 0
         else:
            # this one seem unlikely to get to
            hour = 0
            minute = totalTime
         
      if hour >= 12 and isPm == None:
         isPm = True
      if hour >= 12:
         hour -= 12
      if isPm:
         hour += 12

      return hour*100 + minute
   except:
      raise ValueError('Invalid Time Read.')
      return None

def timeIntToStr(timeInt, useAmPm = False):
   if useAmPm: # 12 Hour with AM / PM
      amPmStr = " AM"
      hour = int(timeInt / 100)
      minute = int(timeInt % 100)
      if hour >= 12:
         amPmStr = " PM"
         if hour >= 13:
            hour -= 12
      elif hour == 0:
         hour = 12
   else: # 24 hour that the web server wants.
      amPmStr = ""
      hour = int(timeInt / 100)
      minute = int(timeInt % 100)

   return "{:02d}:{:02d}".format(hour, minute) + amPmStr

def tryDictSettingToType(convertFunc, settingsDict, dictStr, origVal):
   dictEntryExists = False
   convertFuncSuccess = False
   retVal = origVal

   try:
      dictVal = settingsDict[dictStr]
      dictEntryExists = True
   except:
      pass

   if dictEntryExists:
      try:
         retVal = convertFunc(dictVal)
         convertFuncSuccess = True
      except:
         pass
   
   return [dictEntryExists, convertFuncSuccess, retVal]

def getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted):
   return [allValid and exists and converted, allAvailValid and (converted or not exists), anyValid or converted]

def dictToClass(settingsDict, settingsClass):
   allValid = True
   allAvailValid = True
   anyValid = False

   exists = False
   converted = False
   val = None

   [exists, converted, val] = tryDictSettingToType(float, settingsDict, 'MinTimeBetweenChangingSwitchState', settingsClass.MIN_TIME_BETWEEN_CHANGING_SWITCH_STATE)
   settingsClass.MIN_TIME_BETWEEN_CHANGING_SWITCH_STATE = val
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   [exists, converted, val] = tryDictSettingToType(float, settingsDict, 'MinTimeBetweenRetryingSwitchChange', settingsClass.MIN_TIME_BETWEEN_RETRYING_SWITCH_CHANGE)
   settingsClass.MIN_TIME_BETWEEN_RETRYING_SWITCH_CHANGE = val
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   [exists, converted, val] = tryDictSettingToType(float, settingsDict, 'TimeBetweenTempCheck', settingsClass.TIME_BETWEEN_TEMPERATURE_CHECK)
   settingsClass.TIME_BETWEEN_TEMPERATURE_CHECK = val
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   [exists, converted, val] = tryDictSettingToType(float, settingsDict, 'SwitchOnTemp', settingsClass.SWITCH_ON_TEMPERATURE)
   settingsClass.SWITCH_ON_TEMPERATURE = val
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   [exists, converted, val] = tryDictSettingToType(float, settingsDict, 'SwitchOffTemp', settingsClass.SWITCH_OFF_TEMPERATURE)
   settingsClass.SWITCH_OFF_TEMPERATURE = val
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   [exists, converted, val] = tryDictSettingToType(str, settingsDict, 'SmartPlugIpAddr', settingsClass.SMART_PLUG_IP_ADDR)
   settingsClass.SMART_PLUG_IP_ADDR = val
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   [exists, converted, val] = tryDictSettingToType(strToTimeInt, settingsDict, 'TimeOfDayToStart', settingsClass.TIME_OF_DAY_TO_START)
   settingsClass.TIME_OF_DAY_TO_START = val
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   [exists, converted, val] = tryDictSettingToType(strToTimeInt, settingsDict, 'TimeOfDayToStop', settingsClass.TIME_OF_DAY_TO_STOP)
   settingsClass.TIME_OF_DAY_TO_STOP = val
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   [exists, converted, val] = tryDictSettingToType(float, settingsDict, 'InvalidTempLow', settingsClass.INVALID_TEMPERATURE_LOW)
   settingsClass.INVALID_TEMPERATURE_LOW = val
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   [exists, converted, val] = tryDictSettingToType(float, settingsDict, 'InvalidTempHigh', settingsClass.INVALID_TEMPERATURE_HIGH)
   settingsClass.INVALID_TEMPERATURE_HIGH = val
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   [exists, converted, val] = tryDictSettingToType(str, settingsDict, 'DeviceName', settingsClass.DEVICE_NAME)
   settingsClass.DEVICE_NAME = val
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   [exists, converted, val] = tryDictSettingToType(str, settingsDict, 'DeviceColor', settingsClass.DEVICE_COLOR)
   settingsClass.DEVICE_COLOR = val
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   # Do SwitchStateAfterTimeOfDayStop last so we can do a little extra conversion.
   [exists, converted, val] = tryDictSettingToType(str, settingsDict, 'SwitchStateAfterTimeOfDayStop', settingsClass.SWITCH_STATE_AFTER_TIME_OF_DAY_STOP)
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   if converted:
      # Determine what to set the switch to when entering the time of day to stop controlling the switch.
      finalSwitchStateStr = val.lower()
      if finalSwitchStateStr == 'off':
         settingsClass.SWITCH_STATE_AFTER_TIME_OF_DAY_STOP = False
      elif finalSwitchStateStr == 'on':
         settingsClass.SWITCH_STATE_AFTER_TIME_OF_DAY_STOP = True
      else:
         settingsClass.SWITCH_STATE_AFTER_TIME_OF_DAY_STOP = None

   # This should be the last thing (since it is calculated from other ini values).
   if settingsClass.TIME_BETWEEN_TEMPERATURE_CHECK != None:
      settingsClass.TEMPERATURE_AVERAGE_TIME_AMOUNT = settingsClass.TIME_BETWEEN_TEMPERATURE_CHECK * 5
   else:
      settingsClass.TEMPERATURE_AVERAGE_TIME_AMOUNT = None

   return [allValid, allAvailValid, anyValid]

def floatToIntStr(floatVal):
   if floatVal > 0.0:
      return str(int(floatVal + 0.5))
   elif floatVal < 0.0:
      return str(-int(-floatVal + 0.5))
   else:
      return str(0)

def tempToTimeStr(tempVal):
   if float(int(tempVal)) == float(tempVal):
      return str(int(tempVal))
   else:
      return "{:.1f}".format(tempVal)

def safeConvertToStr(convertFunc, inVal, failRetVal = ""):
   retVal = failRetVal
   try:
      retVal = convertFunc(inVal)
   except:
      pass
   return retVal

def switchStateAfterTimeOfDayStop_toStr(SwitchStateAfterTimeOfDayStop_val):
   if SwitchStateAfterTimeOfDayStop_val == False:
      retVal = 'Off'
   elif SwitchStateAfterTimeOfDayStop_val == True:
      retVal = 'On'
   else:
      retVal = 'No Change'
   return retVal

def classToDict(settingsClass, settingsDict):
   settingsDict['MinTimeBetweenChangingSwitchState'] = safeConvertToStr(floatToIntStr, settingsClass.MIN_TIME_BETWEEN_CHANGING_SWITCH_STATE)
   settingsDict['MinTimeBetweenRetryingSwitchChange'] = safeConvertToStr(floatToIntStr, settingsClass.MIN_TIME_BETWEEN_RETRYING_SWITCH_CHANGE)
   
   settingsDict['TimeBetweenTempCheck'] = safeConvertToStr(floatToIntStr, settingsClass.TIME_BETWEEN_TEMPERATURE_CHECK)
   
   settingsDict['SwitchOnTemp'] = safeConvertToStr(tempToTimeStr, settingsClass.SWITCH_ON_TEMPERATURE)
   settingsDict['SwitchOffTemp'] = safeConvertToStr(tempToTimeStr, settingsClass.SWITCH_OFF_TEMPERATURE)

   settingsDict['SmartPlugIpAddr'] = settingsClass.SMART_PLUG_IP_ADDR
   
   settingsDict['TimeOfDayToStart'] = safeConvertToStr(timeIntToStr, settingsClass.TIME_OF_DAY_TO_START)
   settingsDict['TimeOfDayToStop'] = safeConvertToStr(timeIntToStr, settingsClass.TIME_OF_DAY_TO_STOP)
   
   settingsDict['InvalidTempLow'] = safeConvertToStr(tempToTimeStr, settingsClass.INVALID_TEMPERATURE_LOW)
   settingsDict['InvalidTempHigh'] = safeConvertToStr(tempToTimeStr, settingsClass.INVALID_TEMPERATURE_HIGH)
   
   # Determine what to set the switch to when entering the time of day to stop controlling the switch.
   settingsDict['SwitchStateAfterTimeOfDayStop'] = switchStateAfterTimeOfDayStop_toStr(settingsClass.SWITCH_STATE_AFTER_TIME_OF_DAY_STOP)

   settingsDict['DeviceName'] = settingsClass.DEVICE_NAME
   settingsDict['DeviceColor'] = settingsClass.DEVICE_COLOR

def loadSettingsFromJson():
   global currentTempCtrlSettings
   global currentTempCtrlDict

   success = True
   try:
      currentTempCtrlDict = json.loads(readWholeFile(JSON_PATH))
      success = dictToClass(currentTempCtrlDict, currentTempCtrlSettings)[0] # [0] is allValid
   except:
      success = False
   return success


def printTempCtrlSettings(tempCtrlSettings):
   try:
      degreeSign= u'\N{DEGREE SIGN}'
      timeUnit = " sec"
      tempUnit = " " + '' + "F"
      # Print in opposite order to make it appear in the correct order in the short log (i.e. last print at top)
      logMsg("Temp Avg Time           = " + str(tempCtrlSettings.TEMPERATURE_AVERAGE_TIME_AMOUNT) + timeUnit)
      logMsg("Switch State After      = " + switchStateAfterTimeOfDayStop_toStr(tempCtrlSettings.SWITCH_STATE_AFTER_TIME_OF_DAY_STOP))
      logMsg("Invalid Temp High       = " + str(tempCtrlSettings.INVALID_TEMPERATURE_HIGH) + tempUnit)
      logMsg("Invalid Tem Low         = " + str(tempCtrlSettings.INVALID_TEMPERATURE_LOW)+ tempUnit)
      logMsg("Temp Check Time         = " + str(tempCtrlSettings.TIME_BETWEEN_TEMPERATURE_CHECK) + timeUnit)
      logMsg("Min Switch Retry Time   = " + str(tempCtrlSettings.MIN_TIME_BETWEEN_RETRYING_SWITCH_CHANGE) + timeUnit)
      logMsg("Min Switch Toggle Time  = " + str(tempCtrlSettings.MIN_TIME_BETWEEN_CHANGING_SWITCH_STATE) + timeUnit)
      logMsg("Smart Plug Ip Addr      = " + str(tempCtrlSettings.SMART_PLUG_IP_ADDR))
      logMsg("Off Temp                = " + str(tempCtrlSettings.SWITCH_OFF_TEMPERATURE) + tempUnit)
      logMsg("On Temp                 = " + str(tempCtrlSettings.SWITCH_ON_TEMPERATURE) + tempUnit)
      logMsg("Stop Time               = " + timeIntToStr(tempCtrlSettings.TIME_OF_DAY_TO_STOP, True))
      logMsg("Start Time              = " + timeIntToStr(tempCtrlSettings.TIME_OF_DAY_TO_START, True))
      logMsg("Device Color            = " + str(tempCtrlSettings.DEVICE_COLOR))
      logMsg("Device Name             = " + str(tempCtrlSettings.DEVICE_NAME))
   except:
      pass



################################################################################
# IPC Server For New Json Settings
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

def updateSettingsFromDict(newSettingsDict):
   global currentTempCtrlDict
   global currentTempCtrlSettings
   try:
      newTempCtrlSettings = copy.copy(currentTempCtrlSettings) # pass in a copy of the current settings. dictToClass will only change the settings that are valid from the dict.
      success = dictToClass(newSettingsDict, newTempCtrlSettings)[2] # [2] is the anyValid flag. If set some settings passed in where valid (i.e. newTempCtrlSettings was updated)
      if success and currentTempCtrlSettings != newTempCtrlSettings:
         currentTempCtrlSettings = newTempCtrlSettings
         classToDict(newTempCtrlSettings, currentTempCtrlDict)

         logMsg("### Recieved New Settings")
         printTempCtrlSettings(currentTempCtrlSettings)
         writeWholeFile(JSON_PATH, json.dumps(currentTempCtrlDict, indent=3))
      elif success:
         logMsg("##### Recieved Same Settings")
      elif not success:
         logMsg("##### Recieved Invalid Settings")

   except:
      pass

def getStatus(): # Returns Dictionary
   global lastTemperatureAverage
   global currentSwitchState
   status = dict()

   switchStateString = "Unknown"
   if currentSwitchState != None and currentSwitchState == True:
      switchStateString = "On"
   elif currentSwitchState != None and currentSwitchState == False:
      switchStateString = "Off"
   
   try:
      status['Temp'] = "{:.1f}".format(lastTemperatureAverage)
   except:
      status['Temp'] = ""
   status['SwitchState'] = switchStateString

   return status

def getIpcResonseJsonStr():
   global currentTempCtrlSettings
   global currentTempCtrlDict

   statusDict = getStatus()
   settingsDict = dict()
   
   try:
      classToDict(currentTempCtrlSettings, settingsDict)
   except:
      settingsDict = currentTempCtrlDict
   
   retVal = ""
   try:
      combinedDict = dict()
      combinedDict['status'] = statusDict
      combinedDict['settings'] = settingsDict
      retVal = json.dumps(combinedDict)
   except:
      logMsg("##### Something very bad happened: getIpcResonseJsonStr")

   return retVal


def ipcMessageCallback(objects):
   global currentTempCtrlDict
   global currentTempCtrlSettings

   global settingsMutex
   settingsMutex.acquire() # Lock Mutex

   # Try to parse the input message as a json.
   useNewSettings = True
   try:
      newSettingsDict = json.loads(objects[0].properties['json'])
   except:
      useNewSettings = False

   # Try to use the new settings.
   if useNewSettings:
      updateSettingsFromDict(newSettingsDict)

   # Respond with the current settings.
   response = [Response(getIpcResonseJsonStr())]

   settingsMutex.release() # Unlock Mutex

   return response

def runIpcServer(socketPath):
   ipc.Server(socketPath, ipcMessageCallback).serve_forever()

def setupIcpServer(socketPath):
   if os.path.exists(socketPath):
      os.remove(socketPath)
   t = Thread(target=runIpcServer, args=(socketPath,))
   t.start()

   # Make sure the socket file is accessible by the webserver.
   for i in range(100):
      if os.path.exists(socketPath):
         os.system('chmod 666 ' + socketPath) # allow anyone to read/write
         break
      else:
         time.sleep(0.1)


################################################################################
# Temperature Helper Functions
################################################################################
def getTemperature(tempCtrlSettings):
   curTemperature = temperatureSensorLib.temperatureSensor_getFahrenheit()
   
   retVal = curTemperature
   
   try:
      global temperatureStoreValuesForAverage
      global lastTemperatureValue
      global lastTemperatureAverage
      
      lastTemperatureValue = curTemperature

      if curTemperature != None:
         if curTemperature > tempCtrlSettings.INVALID_TEMPERATURE_HIGH or curTemperature < tempCtrlSettings.INVALID_TEMPERATURE_LOW:
            logMsg("Invalid temperature from sensor: " + str(curTemperature))
            curTemperature = None
         else:
            temperatureStoreValuesForAverage.append(curTemperature)
      else:
         logMsg("Failed to read from temperature sensor.")
   
      # Remove old temperature values from the list.
      maxNumValuesToStore = int(math.ceil(tempCtrlSettings.TEMPERATURE_AVERAGE_TIME_AMOUNT / tempCtrlSettings.TIME_BETWEEN_TEMPERATURE_CHECK))
      if len(temperatureStoreValuesForAverage) >= maxNumValuesToStore:
         temperatureStoreValuesForAverage = temperatureStoreValuesForAverage[-maxNumValuesToStore:]
      
      # Compute the average temperature from all the values in the list.
      averageSum = 0
      for temp in temperatureStoreValuesForAverage:
         averageSum += temp
      averageTemperature = averageSum / len(temperatureStoreValuesForAverage)

      retVal = averageTemperature
      
      lastTemperatureAverage = averageTemperature
   except:
      logMsg("Failed somewhere in computing average temperature.")
   
   return retVal

def determineIfSwitchStateNeedsToBeSet(temperature, tempCtrlSettings):
   retVal = SWITCH_STATE_NO_CHANGE
   
   try:
      if tempCtrlSettings.SWITCH_ON_TEMPERATURE > tempCtrlSettings.SWITCH_OFF_TEMPERATURE:
         if temperature >= tempCtrlSettings.SWITCH_ON_TEMPERATURE:
            retVal = SWITCH_STATE_ON
         elif temperature <= tempCtrlSettings.SWITCH_OFF_TEMPERATURE:
            retVal = SWITCH_STATE_OFF
      else:
         if temperature <= tempCtrlSettings.SWITCH_ON_TEMPERATURE:
            retVal = SWITCH_STATE_ON
         elif temperature >= tempCtrlSettings.SWITCH_OFF_TEMPERATURE:
            retVal = SWITCH_STATE_OFF
   except:
      logMsg("Failed to determine if the switch state needs to be set.")
   return retVal
      


################################################################################
# Smart Plug Helper Functions
################################################################################
def setSmartPlugState_withCheck(switchState, tempCtrlSettings):
   global currentSwitchState
   # Check for situation where we need to return silently. This is used for situations where no smart switch exists, but the temperature sensor is being manually monitored.
   if tempCtrlSettings.SMART_PLUG_IP_ADDR == None or tempCtrlSettings.SMART_PLUG_IP_ADDR == "":
      currentSwitchState = True if switchState == SWITCH_STATE_ON else False
      return CHANGE_SWITCH_RESULT_SUCCESS_NO_CHANGE_NEEDED

   retVal = CHANGE_SWITCH_RESULT_FAILED

   try:
      desiredSwitchState = False # False for off, True for on
      if switchState == SWITCH_STATE_ON:
         desiredSwitchState = True
      
      currentSwitchState = smartPlugLib.smartPlug_getState(tempCtrlSettings.SMART_PLUG_IP_ADDR)
      
      if currentSwitchState != None:
         if currentSwitchState != desiredSwitchState:
            logMsg("Changing switch state to: " + str(switchState))

            time.sleep(1) # Just talked to the switch to determine status. Wait a moment before setting the new state. (Probably not necessary, but shouldn't hurt either.)
            success = smartPlugLib.smartPlug_onOff(tempCtrlSettings.SMART_PLUG_IP_ADDR, desiredSwitchState)
            
            if success:
               retVal = CHANGE_SWITCH_RESULT_SUCCESS_SWITCH_STATE_CHANGED
         else:
            retVal = CHANGE_SWITCH_RESULT_SUCCESS_NO_CHANGE_NEEDED
      else:
         logMsg("Failed to determine the current state of the switch.")

   except:
      logMsg("Failed somewhere in the process of setting the state of the switch.")
      
   return retVal


def setSmartPlugState_withoutCheck(switchState, tempCtrlSettings):
   global currentSwitchState
   # Check for situation where we need to return silently. This is used for situations where no smart switch exists, but the temperature sensor is being manually monitored.
   if tempCtrlSettings.SMART_PLUG_IP_ADDR == None or tempCtrlSettings.SMART_PLUG_IP_ADDR == "":
      currentSwitchState = True if switchState == SWITCH_STATE_ON else False
      return CHANGE_SWITCH_RESULT_SUCCESS_NO_CHANGE_NEEDED

   retVal = CHANGE_SWITCH_RESULT_FAILED

   try:
      desiredSwitchState = False # False for off, True for on
      if switchState == SWITCH_STATE_ON:
         desiredSwitchState = True
      
      switchStateIsChanging = False
      if currentSwitchState != None and currentSwitchState == desiredSwitchState:
         pass # Nothing to do
      else:
         logMsg("Changing switch state to: " + str(switchState))
         switchStateIsChanging = True
      
      success = smartPlugLib.smartPlug_onOff(tempCtrlSettings.SMART_PLUG_IP_ADDR, desiredSwitchState)
      
      if success:
         currentSwitchState = desiredSwitchState
         if switchStateIsChanging:
            retVal = CHANGE_SWITCH_RESULT_SUCCESS_SWITCH_STATE_CHANGED
         else:
            retVal = CHANGE_SWITCH_RESULT_SUCCESS_NO_CHANGE_NEEDED

   except:
      logMsg("Failed somewhere in the process of setting the state of the switch.")
      
   return retVal


################################################################################
# Time Helper Functions
################################################################################
def getSleepTimeUntilNextTemperatureCheckTime(tempCtrlSettings):
   global nextTemperatureCheckTime
   sleepTime = tempCtrlSettings.TIME_BETWEEN_TEMPERATURE_CHECK

   try:
      # Determine the next time to check the temperature.
      nextTemperatureCheckTime += tempCtrlSettings.TIME_BETWEEN_TEMPERATURE_CHECK
      currentTime = getCurrentTime()
      while nextTemperatureCheckTime < currentTime:
         nextTemperatureCheckTime += tempCtrlSettings.TIME_BETWEEN_TEMPERATURE_CHECK
      
      # Sleep until the next time to check the temperature.
      sleepTime = nextTemperatureCheckTime - currentTime
   except:
      logMsg("Failed to determine sleep amount, using default.")
   return sleepTime
   
def isItTimeOfDayToControlSwitch(tempCtrlSettings):
   retVal = False
   
   try:
      timeFormatStr = "%H%M" # Note: default time format string is "%c"
      now = time.strftime(timeFormatStr)
      timestamp = "{}".format(now)
      
      nowTimeOfDay = int(timestamp)

      if tempCtrlSettings.TIME_OF_DAY_TO_START > tempCtrlSettings.TIME_OF_DAY_TO_STOP:
         # Start in 1 day and ends in the next day
         if nowTimeOfDay >= tempCtrlSettings.TIME_OF_DAY_TO_START or nowTimeOfDay < tempCtrlSettings.TIME_OF_DAY_TO_STOP:
            retVal = True
      else:
         # Start and end in same day
         if nowTimeOfDay >= tempCtrlSettings.TIME_OF_DAY_TO_START and nowTimeOfDay < tempCtrlSettings.TIME_OF_DAY_TO_STOP:
            retVal = True
   except:
      logMsg("Failed to determine time of day.")

   return retVal
      

################################################################################
# Program Start
################################################################################

# Initialization
logMsg("##### Starting Temperature Control Switch #####")

goodSettings = loadSettingsFromJson()
printTempCtrlSettings(currentTempCtrlSettings)

setupIcpServer(IPC_SOCKET_PATH)

if goodSettings == False:
   logMsg("##### Invalid Starting Settings - Waiting for valid settings.")
while goodSettings == False:
   time.sleep(10)
   goodSettings = loadSettingsFromJson()
   if goodSettings:
      logMsg("##### Valid Start Settings Found #####")

temperatureSensorLib.temperatureSensor_init()
temperatureSensorLib.temperatureSensor_getFahrenheit() # It seems like the first temperature can be old, clear out the old value.

nextTemperatureCheckTime = getCurrentTime()

setSmartPlugState = setSmartPlugState_withoutCheck

# Start Forever Loop
while 1:
   settingsMutex.acquire()
   tempCtrlSettings = copy.copy(currentTempCtrlSettings) # Copy the settings off for use during this loop through the while 1
   settingsMutex.release()

   temperature = getTemperature(tempCtrlSettings)
   
   if temperature != None:
      extraLog = ""
      try:
         
         if isItTimeOfDayToControlSwitch(tempCtrlSettings):
            # Check if it is ok to modify the switch state (based on the current time).
            currentTime = getCurrentTime()
            timeSinceLastSwitchChangeFailure = currentTime - lastFailedSwitchChangeTime
            timeSinceLastSwitchChangeSuccess = currentTime - lastSuccessfulSwitchChangeTime
            
            if timeSinceLastSwitchChangeFailure > tempCtrlSettings.MIN_TIME_BETWEEN_RETRYING_SWITCH_CHANGE and \
               timeSinceLastSwitchChangeSuccess > tempCtrlSettings.MIN_TIME_BETWEEN_CHANGING_SWITCH_STATE:
   
               switchChange = determineIfSwitchStateNeedsToBeSet(temperature, tempCtrlSettings)
               
               if switchChange == SWITCH_STATE_ON or switchChange == SWITCH_STATE_OFF:
                  result = setSmartPlugState(switchChange, tempCtrlSettings)
                  
                  if result == CHANGE_SWITCH_RESULT_FAILED:
                     lastFailedSwitchChangeTime = getCurrentTime()
                     lastSuccessfulSwitchChangeTime = 0
   
                  elif result == CHANGE_SWITCH_RESULT_SUCCESS_SWITCH_STATE_CHANGED or result == CHANGE_SWITCH_RESULT_SUCCESS_NO_CHANGE_NEEDED:
                     lastSuccessfulSwitchChangeTime = getCurrentTime()
                     lastFailedSwitchChangeTime = 0
                  
                  extraLog = result
               else:
                  extraLog = switchChange
            else:
               timeUntilSwitchCanBeSet = max(tempCtrlSettings.MIN_TIME_BETWEEN_RETRYING_SWITCH_CHANGE - timeSinceLastSwitchChangeFailure, \
                                             tempCtrlSettings.MIN_TIME_BETWEEN_CHANGING_SWITCH_STATE - timeSinceLastSwitchChangeSuccess)
               extraLog = "Can't set switch for {:3d} seconds".format(int(timeUntilSwitchCanBeSet))
            
            activeDuringTimeOfDayToControlSwitch = True
         else:
            if activeDuringTimeOfDayToControlSwitch:
               extraLog = "Leaving time to control switch - "
               
               if tempCtrlSettings.SWITCH_STATE_AFTER_TIME_OF_DAY_STOP != None:
                  timeSinceLastSwitchChangeFailure = getCurrentTime() - lastFailedSwitchChangeTime
                  if timeSinceLastSwitchChangeFailure > tempCtrlSettings.MIN_TIME_BETWEEN_RETRYING_SWITCH_CHANGE:
                     newSwitchState = SWITCH_STATE_ON if tempCtrlSettings.SWITCH_STATE_AFTER_TIME_OF_DAY_STOP else SWITCH_STATE_OFF
                     result = setSmartPlugState(newSwitchState, tempCtrlSettings)
                     if result != CHANGE_SWITCH_RESULT_FAILED:
                        activeDuringTimeOfDayToControlSwitch = False
                        extraLog += ("Succeeded in setting switch state to: " + newSwitchState)
                     else:
                        lastFailedSwitchChangeTime = getCurrentTime()
                        extraLog += ("Failed to set switch state to: " + newSwitchState)
                  else:
                     extraLog += "Last switch setting failed, waiting to retry."
               else:
                  activeDuringTimeOfDayToControlSwitch = False
                  extraLog += "No change of switch specified."
            else:
               extraLog = "Not controlling switch at this time."
               
         
         logMsg("Temperature = {: 3.1f} | ".format(temperature) + extraLog, True)

         # Log temperature and switch state.
         lastTemperatureLogTime = updateTemperatureLogFile(temperature, currentSwitchState, lastTemperatureLogTime)
      except:
         logMsg("Failed somewhere in the while 1 loop.")

   else:
      logMsg("Failed to read temperature!")

   # Use the most up-to-date settings for the while 1 sleep.
   settingsMutex.acquire()
   sleepTime = getSleepTimeUntilNextTemperatureCheckTime(currentTempCtrlSettings)
   settingsMutex.release()

   time.sleep(sleepTime)
