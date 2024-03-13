import os
import json

# Parameters for making the log files that store the raw MQTT data
MQTT_LOG_BASE_DIR = ''
MQTT_LOG_DIR_CHMOD = '777'
MQTT_LOG_FILE_CHMOD = '666'

THIS_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

CHART_ARRAY_PY = "getTempChartArray.py"

with open(os.path.join(THIS_SCRIPT_DIR, "mqttLoggerSubs.json")) as subsJsonFile:
   subsJson = json.load(subsJsonFile)

   checkStartScript = os.path.join(THIS_SCRIPT_DIR, "checkStart.py")
   mqttLoggerScript = os.path.join(THIS_SCRIPT_DIR, "mqttLogger.py")

   for subRelPath in subsJson["subscriptions"]:
      subPath = os.path.join(THIS_SCRIPT_DIR, subRelPath)

      if os.path.exists(subPath): # Make sure the json file exists
         with open(subPath) as singleSubJsonFile: # Open the json file
            # Get topic name
            singleSubJson = json.load(singleSubJsonFile)
            topic = singleSubJson["TopicName"]

            # Create log directory.
            logFileBase = os.path.join(MQTT_LOG_BASE_DIR, topic)
            logFileDir, logFileNameBase = os.path.split(logFileBase)
            if not os.path.exists(logFileDir):
               os.makedirs(logFileDir)
               os.system(f"chmod {MQTT_LOG_DIR_CHMOD} {logFileDir}") # Set directory permissions

            # Create the log files.
            def makeLogFile(logFileDir, logFileName):
               logFileName = os.path.join(logFileDir, logFileName)
               if not os.path.exists(logFileName):
                  os.system(f"touch {logFileName}")
                  os.system(f"chmod {MQTT_LOG_FILE_CHMOD} {logFileName}") # Set log file permissions
            makeLogFile(logFileDir, logFileNameBase + ".lock")
            makeLogFile(logFileDir, logFileNameBase + ".log")

            # Copy the Chart Array Script
            chartArrayFinalPath = os.path.join(MQTT_LOG_BASE_DIR, CHART_ARRAY_PY)
            if not os.path.exists(chartArrayFinalPath):
               os.system(f"cp {os.path.join(THIS_SCRIPT_DIR, CHART_ARRAY_PY)} {chartArrayFinalPath}")
               os.system(f"chmod 777 {chartArrayFinalPath}")

            # Start the logging subscriber
            cmd = f'python3 {checkStartScript} --pathToScript {mqttLoggerScript} --argsToScript "-c {subPath}"'
            print(cmd)
            os.system(f"{cmd} &") # add & to make the detach to process from this one.
   