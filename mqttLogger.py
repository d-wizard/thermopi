import os
import time
import json
import random
from datetime import datetime

from paho.mqtt import client as mqtt_client
from getTempChartArray import updateTemperatureLogFile


################################################################################
# Setting Specified Via The .json File
################################################################################

class topicLogSettings(object):
   def __init__(self):
      self.TopicName = None
      self.NumPointsToAverage = None
      self.LogFilePath = None
      
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
JSON_PATH = THIS_SCRIPT_FILENAME_NO_EXT + '.json'


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

def loadSettingsFromJson():
   global currentSettings

   success = True
   try:
      jsonFromFileSystem = json.loads(readWholeFile(JSON_PATH))
      success = dictToClass(jsonFromFileSystem, currentSettings)[0] # [0] is allValid
   except:
      success = False
   return success

################################################################################
# MQTT Logger Helper Functions
################################################################################
def logMqttData(mqttData, ctrlSettings):
   mqttData = strToFloat(mqttData)
   if mqttData == None:
      return

   try:
      logFileVal = None
      if ctrlSettings.NumPointsToAverage != None and ctrlSettings.NumPointsToAverage > 0:
         global mqttStoreValuesForAverage
         mqttStoreValuesForAverage.append(mqttData)

         # Remove old values from the list.
         if len(mqttStoreValuesForAverage) >= ctrlSettings.NumPointsToAverage:
            mqttStoreValuesForAverage = mqttStoreValuesForAverage[-ctrlSettings.NumPointsToAverage:]

         # Compute the average temperature from all the values in the list.
         averageSum = 0
         for temp in mqttStoreValuesForAverage:
            averageSum += temp
         logFileVal = averageSum / len(mqttStoreValuesForAverage)

      else:
         logFileVal = mqttData

      global lastMqttLogTime
      lastMqttLogTime = updateTemperatureLogFile(logFileVal, 0, lastMqttLogTime, ctrlSettings.LogFilePath)
   except:
      logMsg("Failed somewhere in logging MQTT Data.")

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
      logMqttData(msg.payload.decode(), ctrlSettings)

   client.subscribe(ctrlSettings.TopicName)
   client.on_message = mqtt_onMessage


################################################################################
# Program Start
################################################################################

# Initialization
logMsg("##### Starting MQTT Logger #####")

goodSettings = loadSettingsFromJson()

if goodSettings == False:
   logMsg("##### Invalid Starting Settings - Waiting for valid settings.")
   exit(0)

# Run MQTT
mqttClient = mqttConnect(currentSettings)
mqttClient.loop_start()
mqttSubscribe(mqttClient, currentSettings)

# Start Forever Loop (everything is done in other threads).
while 1:
    time.sleep(100000)

