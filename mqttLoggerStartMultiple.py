import os
import json

# Parameters for making the log files that store the raw MQTT data
MQTT_LOG_BASE_DIR = ''
MQTT_LOG_DIR_CHMOD = '777'
MQTT_LOG_FILE_CHMOD = '666'

THIS_SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

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
            def makeLogFile(logFileName):
               if not os.path.exists(logFileName):
                  os.system(f"touch {logFileName}")
                  os.system(f"chmod {MQTT_LOG_FILE_CHMOD} {logFileName}") # Set log file permissions
            makeLogFile(os.path.join(logFileDir, logFileNameBase + ".lock"))
            makeLogFile(os.path.join(logFileDir, logFileNameBase + ".log"))

            # Start the logging subscriber
            cmd = f'python3 {checkStartScript} --pathToScript {mqttLoggerScript} --argsToScript "-c {subPath}"'
            print(cmd)
            os.system(f"{cmd} &") # add & to make the detach to process from this one.
   