import os
import time
import json
import random
import argparse
from datetime import datetime
from paho.mqtt import client as mqtt_client

from getTempChartArray import updateTemperatureLogFile
from getTempChartArray import getTopicLogFilePath


################################################################################
# Setting Specified Via The .json File
################################################################################

class topicLogSettings(object):
   def __init__(self):
      self.TopicName = None
      self.NumPointsToAverage = 1
      self.LogFilePath = None
      self.MinTimeBetweenLogUpdates = 30
      
      self.MqttBrokerIp = None
      self.MqttBrokerPort = None
      self.MqttUserName = ""
      self.MqttPassword = ""
      self.MqttClientId = ""


currentSettings = topicLogSettings()

################################################################################
# Constant Variables
################################################################################
THIS_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
THIS_SCRIPT_FILENAME_NO_EXT = os.path.splitext(os.path.realpath(__file__))[0]


################################################################################
# Global Variables
################################################################################
mqttStoreValuesForAverage = []
lastMqttValue   = None
lastMqttAverage = None
lastMqttLogTime = 0

logNewLine = '\n'
logMaxLogLines_short = 5000
logLineToLeaveAfterTrim_short = 3000
logMaxLogLines_long = 50000
logLineToLeaveAfterTrim_long = 30000


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

def strToFloat(inStr):
   try:
      return float(inStr)
   except:
      return None



################################################################################
# JSON Functions
################################################################################
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

   [exists, converted, val] = tryDictSettingToType(str, settingsDict, 'TopicName', settingsClass.TopicName)
   settingsClass.TopicName = val
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   [exists, converted, val] = tryDictSettingToType(int, settingsDict, 'NumPointsToAverage', settingsClass.NumPointsToAverage)
   settingsClass.NumPointsToAverage = val
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   [exists, converted, val] = tryDictSettingToType(int, settingsDict, 'MinTimeBetweenLogUpdates', settingsClass.MinTimeBetweenLogUpdates)
   settingsClass.MinTimeBetweenLogUpdates = val
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   [exists, converted, val] = tryDictSettingToType(str, settingsDict, 'LogFilePath', settingsClass.LogFilePath)
   settingsClass.LogFilePath = val
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   # MQTT Broker Params
   [exists, converted, val] = tryDictSettingToType(str, settingsDict, 'MqttBrokerIp', settingsClass.MqttBrokerIp)
   settingsClass.MqttBrokerIp = val
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   [exists, converted, val] = tryDictSettingToType(int, settingsDict, 'MqttBrokerPort', settingsClass.MqttBrokerPort)
   settingsClass.MqttBrokerPort = val
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   [exists, converted, val] = tryDictSettingToType(str, settingsDict, 'MqttUserName', settingsClass.MqttUserName)
   settingsClass.MqttUserName = val
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   [exists, converted, val] = tryDictSettingToType(str, settingsDict, 'MqttPassword', settingsClass.MqttPassword)
   settingsClass.MqttPassword = val
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   [exists, converted, val] = tryDictSettingToType(str, settingsDict, 'MqttClientId', settingsClass.MqttClientId)
   settingsClass.MqttClientId = val
   [allValid, allAvailValid, anyValid] = getValidDictToClass(allValid, allAvailValid, anyValid, exists, converted)

   return [allValid, allAvailValid, anyValid]

def loadSettingsFromJson(pathToJson):
   global currentSettings

   success = True
   try:
      jsonFromFileSystem = json.loads(readWholeFile(pathToJson))
      success = dictToClass(jsonFromFileSystem, currentSettings)[1] # [1] is allAvailValid

      if currentSettings.LogFilePath == None and currentSettings.TopicName != None:
         # If LogFilePath wasn't specified, determine its value from the topic name
         currentSettings.LogFilePath = getTopicLogFilePath(currentSettings.TopicName)

      # Make sure certain values have been filled in.
      if currentSettings.TopicName == None or currentSettings.LogFilePath == None or \
         currentSettings.MqttBrokerIp == None or currentSettings.MqttBrokerPort == None:
         success = False

   except:
      success = False
   return success

################################################################################
# MQTT Logger Helper Functions
################################################################################
def logMqttData(mqttData, ctrlSettings):
   delim = ','
   mqttDataStrs = mqttData.split(delim) if delim in mqttData else [mqttData]
   logFileVals = []
   success = True
   for mqttDataIndex in range(len(mqttDataStrs)):
      val = getLogFileValue(mqttDataStrs[mqttDataIndex], mqttDataIndex, ctrlSettings)
      logFileVals.append(val)
      if val == None:
         success = False
   
   # Log the data
   if success:
      global lastMqttLogTime
      lastMqttLogTime = updateTemperatureLogFile(logFileVals, lastMqttLogTime, ctrlSettings.LogFilePath, ctrlSettings.MinTimeBetweenLogUpdates)

def getLogFileValue(mqttDataStr, mqttDataIndex, ctrlSettings):
   mqttData = strToFloat(mqttDataStr)
   logFileVal = None

   try:
      if ctrlSettings.NumPointsToAverage != None and ctrlSettings.NumPointsToAverage > 0:
         try:
            global mqttStoreValuesForAverage
            while len(mqttStoreValuesForAverage) <= mqttDataIndex:
               mqttStoreValuesForAverage.append([]) # Put an empty list at the end.

            # Add the new data if it's valid
            if mqttData != None:
               mqttStoreValuesForAverage[mqttDataIndex].append(mqttData)

               # Remove old values from the list.
               if len(mqttStoreValuesForAverage[mqttDataIndex]) >= ctrlSettings.NumPointsToAverage:
                  mqttStoreValuesForAverage[mqttDataIndex] = mqttStoreValuesForAverage[mqttDataIndex][-ctrlSettings.NumPointsToAverage:]

            # Compute the average value from all the values in the list.
            if len(mqttStoreValuesForAverage[mqttDataIndex]) > 0:
               averageSum = 0
               for temp in mqttStoreValuesForAverage[mqttDataIndex]:
                  averageSum += temp
               logFileVal = averageSum / len(mqttStoreValuesForAverage[mqttDataIndex])
         except:
            pass
      else:
         logFileVal = mqttData

   except:
      logMsg("Failed somewhere in logging MQTT Data.")

   # Make sure its a number
   try:
      logFileVal = float(logFileVal)
   except:
      logFileVal = None
   return logFileVal
      

################################################################################
# MQTT Functions
################################################################################
def mqttConnect(ctrlSettings):
   def mqtt_onConnect(client, userdata, flags, rc):
      if rc == 0:
         logMsg("Connected to MQTT Broker!")
      else:
         logMsg("Failed to connect, return code " + str(rc))

   if ctrlSettings.MqttClientId == "":
      ctrlSettings.MqttClientId = f'mqttLogger-{random.randint(0, 100000)}'
   
   # Create the MQTT client.
   client = mqtt_client.Client(ctrlSettings.MqttClientId)
   if ctrlSettings.MqttUserName != "" and ctrlSettings.MqttPassword != "":
      client.username_pw_set(ctrlSettings.MqttUserName, ctrlSettings.MqttPassword)

   client.on_connect = mqtt_onConnect
   client.connect(ctrlSettings.MqttBrokerIp, ctrlSettings.MqttBrokerPort)
   return client

def mqttSubscribe(client: mqtt_client, ctrlSettings):
   def mqtt_onMessage(client, userdata, msg):
      #logMsg(msg.payload.decode())
      logMqttData(msg.payload.decode(), ctrlSettings)

   logMsg("Subscribing to topic: " + ctrlSettings.TopicName)
   client.subscribe(ctrlSettings.TopicName)
   client.on_message = mqtt_onMessage


################################################################################
# Program Start
################################################################################

# Initialization
logMsg("##### Starting MQTT Logger #####")

# Config argparse
parser = argparse.ArgumentParser()
parser.add_argument("-c", type=str, action="store", dest="configJsonPath", help="Path to the JSON with configuration parameters.", default=None)
args = parser.parse_args()

if(args.configJsonPath == None):
   logMsg("Need to specify path to the config JSON.")
   exit(0)

# Make sure to start random number generator at a new point each time this is run.
random.seed()

goodSettings = loadSettingsFromJson(args.configJsonPath)

if goodSettings == False:
   logMsg("##### Invalid Starting Settings - exiting now.")
   exit(0)

# Connect to MQTT Broker
success = False
while not success:
   try:
      mqttClient = mqttConnect(currentSettings)
      success = True
   except:
      time.sleep(15)

# Start the Client loop
success = False
while not success:
   try:
      mqttClient.loop_start()
      success = True
   except:
      time.sleep(15)

# Subscribe to the topic(s)
success = False
while not success:
   try:
      mqttSubscribe(mqttClient, currentSettings)
      success = True
   except:
      time.sleep(15)


# Start Forever Loop (everything is done in other threads).
while 1:
    time.sleep(100000)

