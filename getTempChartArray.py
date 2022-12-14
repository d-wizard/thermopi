import os
import time
import math
from datetime import datetime
import argparse
import fcntl
import json


################################################################################
# Constant Variables
################################################################################
LOG_NEW_LINE = "\n"
LOG_MAX_TIME = 60*60*24*30*2 # 2 Months
LOG_MAX_TIME_TIME_TO_LEAVE_AFTER_TRIM = 60*60*24*7*6 # 6 Weeks

THIS_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
TOPIC_PATH_JSON_NAME = "TopicLogPath.json"

NOW_TIME_TO_USE = None # Default to querying now time

def readWholeFile(path):
   retVal = ""
   try:
      fileId = open(path, 'r')
      retVal = fileId.read()
      fileId.close()
   except:
      pass
   return retVal

def appendFile(path, fileText):
   try:
      fileId = open(path, 'a')
      fileId.write(fileText)
      fileId.close()
   except:
      pass

def writeWholeFile(path, fileText):
   try:
      fileId = open(path, 'w')
      fileId.write(fileText)
      fileId.close()
   except:
      pass

def lockFile(logFilePath):
   fileToLock = os.path.splitext(os.path.realpath(logFilePath))[0] + ".lock"
   fd = open(fileToLock, 'w')
   fcntl.lockf(fd, fcntl.LOCK_EX)
   return fd

def unlockFile(fd):
   fcntl.lockf(fd, fcntl.LOCK_UN )



def timeToPrintStr(unixTime):
   dt = datetime.fromtimestamp(float(unixTime))
   dtStr = str(dt).replace("-", ",").replace(":", ",").replace(" ", ",")
   dtSplit = dtStr.split(",")

   # Convert to integers
   intVals = []
   for strVal in dtSplit:
      intVals.append(int(strVal))

   # Some idiot started months at 0. Not days. Days start at 1. But months start at 0.
   intVals[1] -= 1

   # Convert back to strings
   retStrs = []
   for intVal in intVals:
      retStrs.append(str(intVal))

   return ",".join(retStrs)

def getNowTimeUnix():
   # Check for early return case
   global NOW_TIME_TO_USE
   if NOW_TIME_TO_USE != None:
      return NOW_TIME_TO_USE

   nowUnixTime = time.mktime(datetime.now().timetuple())
   return int(nowUnixTime)

def lineToTime(line):
   try:
      timePart = line.split(",")[0]
   except:
      return None

   try:
      return int(timePart)
   except ValueError:
      timePart = timePart.replace('\x00', '') # I've seen weird situations where a bunch of 0 bytes get mixed in.
      return int(float(timePart)) # Some google results suggest converting to float before int, IDK. This except shouldn't be getting hit very often...

def getUnixTimeToHumanReadable(unixTime):
   if unixTime != None:
      origTimeStr = None
      try:
         # returns YYYY-MM-DD HH:MM:SS
         origTimeStr = str(datetime.fromtimestamp(float((recentTime))))
      except:
         return None
      
      try:
         dayInfo, hourInfo = origTimeStr.split(" ") #YYYY-MM-DD HH:MM:SS
         dayInfo = dayInfo.split("-")
         hourInfo = hourInfo.split(":")
         
         hourInt = int(hourInfo[0])
         AmPmStr = " PM" if hourInt >= 12 else " AM"
         if hourInt == 0:
            hourInt = 12
         elif hourInt > 12:
            hourInt -= 12
         
         # Return in the stupid MM/DD/YY HH:MM:SS XM format Americans use.
         return dayInfo[1] + "/" + dayInfo[2] + "/" + dayInfo[0][-2:] + " " + str(hourInt) + ":" + hourInfo[1] + ":" + hourInfo[2] + AmPmStr
      except:
         return origTimeStr # something strange happened, but the original time string is valid so just return that
   else:
      return None
   return None

def findTimeIndex(lines, timeLimit):
   numLines = len(lines)
   # First test for some error values.
   if lineToTime(lines[0]) >= timeLimit:
      return 0
   if lineToTime(lines[-1]) < timeLimit:
      return -1
   if numLines < 2:
      return -1

   badIndex = 0
   goodIndex = numLines - 1

   bailOut = math.ceil(math.log(numLines, 2))
   bailOut += 4 # Add a few more to the loop; can't hurt.

   while ((goodIndex - badIndex) > 1) and (bailOut > 0):
      tryIndex = int(((goodIndex - badIndex) / 2) + badIndex)
      if lineToTime(lines[tryIndex]) >= timeLimit:
         goodIndex = tryIndex
      else:
         badIndex = tryIndex
      bailOut -= 1

   if bailOut == 0:
      return -1

   return goodIndex

def getLinesToChart(lines, numLinesToChart):
   retVal = []
   numLines = float(len(lines))
   skipOver = numLines / float(numLinesToChart-1)

   if skipOver < 1.0:
      skipOver = 1.0
   
   index = float(0.0)
   while index < numLines:
      retVal.append(lines[int(index)])
      index += skipOver
   
   # Make sure the last time is included.
   if retVal[-1] != lines[-1]:
      retVal.append(lines[-1])

   return retVal

def getPrintStr(lines, indexes = None):
   # If indexes is a single number, make it a list with just that number in it.
   if indexes != None and type(indexes) != list:
      indexes = [indexes] # convert signal value to a list

   retStr = ''
   for line in lines:
      try:
         lineSplit = line.split(",")

         # Start the chart string.
         appendStr = '["Date(' + timeToPrintStr(lineSplit[0]) + ')"' # Start with the unix time

         for valueIndex in range(len(lineSplit)-1):
            # Determine if value should be added to the chart.
            validIndex = (indexes == None) # if indexes insn't specified, all indexes are valid.
            if indexes != None:
               validIndex = valueIndex in indexes # Make sure this value's index is specified in indexes
            
            if validIndex:
               # Don't have the .0 if the temperature value is a whole number (i.e. save 2 bytes)
               tempFlt = float(lineSplit[valueIndex+1])
               tempInt = int(tempFlt)
               tempStr = str(tempInt) if tempInt == tempFlt else str(tempFlt)

               # Add to the chart string
               appendStr += ',' + tempStr
         
         # Finish the chart string
         appendStr += '],'

         retStr += appendStr
      except:
         pass
   
   if retStr[-1] == ',':
       retStr = retStr[:-1]
   return retStr


def updateTemperatureLogFile(temperatureList, timeOfLastTempWrite, logFilePath, minTimeBetweenLogUpdates = 30):
   nowUnixTime = getNowTimeUnix()

   if (nowUnixTime - timeOfLastTempWrite) >= minTimeBetweenLogUpdates:
      timeOfLastTempWrite = nowUnixTime

      # Generate the log line
      logPrint = str(int(nowUnixTime))
      for temperature in temperatureList:
         logPrint += ",{:.1f}".format(temperature)
      logPrint += LOG_NEW_LINE

      lockFd = lockFile(logFilePath)
      appendFile(logFilePath, logPrint)

      # Limit the log from getting too big
      try:
         logLines = readWholeFile(logFilePath).split(LOG_NEW_LINE)
         # remove empty line at end.
         if logLines[-1] == "":
            logLines = logLines[:-1]

         oldestTime = lineToTime(logLines[0])
         if (nowUnixTime - oldestTime) > LOG_MAX_TIME:
            indexToKeep = findTimeIndex(logLines, nowUnixTime - LOG_MAX_TIME_TIME_TO_LEAVE_AFTER_TRIM)
            logLines = logLines[indexToKeep:]
            writeWholeFile(logFilePath, LOG_NEW_LINE.join(logLines)+LOG_NEW_LINE)
      except:
         pass

      unlockFile(lockFd)

   return timeOfLastTempWrite

def getTopicLogFilePath(topicName):
   topicFileName = topicName + ".log"
   topicLogFilePath = os.path.join(THIS_SCRIPT_DIR, topicFileName) # Check if this script is in the MQTT Log file location.

   if os.path.isfile(topicLogFilePath):
      return topicLogFilePath
   else:
      try:
         # Check if the path to the topic logs is specified via JSON
         jsonFromFileSystem = json.loads(readWholeFile(os.path.join(THIS_SCRIPT_DIR, TOPIC_PATH_JSON_NAME)))
   
         topicLogFilePath = os.path.join(jsonFromFileSystem["TopicLogBaseDir"], topicFileName)
         if os.path.isfile(topicLogFilePath):
            return topicLogFilePath
      except:
         pass

   return None


# Main start
if __name__== "__main__":
   # Config argparse
   parser = argparse.ArgumentParser()
   parser.add_argument("-c", type=int, action="store", dest="chartTime", help="Chart Time", default=3600)
   parser.add_argument("-n", type=int, action="store", dest="numPoints", help="Num Points", default=100)
   parser.add_argument("-t", type=str, action="store", dest="topicName", help="MQTT Topic", default=None)
   parser.add_argument("-r", action="store_true", dest="recentValue", help="Only return the most recent value.", default=False)
   parser.add_argument("-l", type=str, action="store", dest="logFilePath", help="Log File Path", default=None)
   parser.add_argument("-o", type=int, action="store", dest="overrideTime", help="Use this to override now time.", default=None)
   parser.add_argument("-i", type=int, action="store", dest="dataIndexToChart", help="The index of the data to chart (0 to N).", default=None)
   args = parser.parse_args()

   logFilePathSpecified = args.logFilePath != None and os.path.isfile(args.logFilePath)

   # Make sure enough info was specified to determine where the log file is.
   if args.topicName == None and logFilePathSpecified == False:
      exit()

   # Determine where the log file is.
   logPath = args.logFilePath if logFilePathSpecified else getTopicLogFilePath(args.topicName)
   if logPath == None or not os.path.isfile(logPath):
      exit()

   # See if the user want to specify "Now Time"
   if args.overrideTime != None:
      try:
         NOW_TIME_TO_USE = int(args.overrideTime)
      except:
         exit()

   # Process the Log File
   lockFd = lockFile(logPath)
   temperatureLogFile = readWholeFile(logPath)
   unlockFile(lockFd)

   lines = temperatureLogFile.split(LOG_NEW_LINE)

   # remove empty line at end.
   if lines[-1] == "":
      lines = lines[:-1]

   if args.recentValue:
      nowUnixTime = getNowTimeUnix()
      recentLogLine = lines[-1]
      recentTime = lineToTime(recentLogLine)
      recentValues = recentLogLine.split(",")[1:] # Strip off the time stamp.

      deltaTime = nowUnixTime - recentTime
      veryOldTimeThreshold = 8*60 # 8 minutes
      goodTimeStr = "1" if deltaTime < veryOldTimeThreshold else "0" # indicate whether this the last value is recent or it is very old
      print(getUnixTimeToHumanReadable(recentTime) + "|" + goodTimeStr + "|" + "|".join(recentValues)) # return Time String|valid_time|sensor_data
   else:
      timeThresh = getNowTimeUnix() - args.chartTime
      index = findTimeIndex(lines, timeThresh)

      if index >= 0:
         lines = lines[index:]

         lines = getLinesToChart(lines, args.numPoints)

         print(getPrintStr(lines, args.dataIndexToChart))
