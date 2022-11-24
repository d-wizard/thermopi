import os
import time
from urllib2 import urlopen
from datetime import datetime

WEATHER_URL = "http://w1.weather.gov/xml/current_obs/display.php?stid=KCID"




################################################################################
# Generic Helper Functions
################################################################################
def appendFile(path, fileText):
   try:
      fileId = open(path, 'a')
      fileId.write(fileText)
      fileId.close()
   except:
      pass

def logMsg(printMsg):
   longTimeStr  = str(datetime.now())
   logMsg = '[' + longTimeStr + "] " + printMsg
   print(logMsg)
   
   logPath = os.path.splitext(os.path.realpath(__file__))[0] + '.log'
   appendFile(logPath, logMsg + '\n')


################################################################################
# API Functions
################################################################################
def getTempFromWeb(url = WEATHER_URL):
   temperature = None
   try:
      webURL = urlopen(WEATHER_URL)
      fullXml = webURL.read()
      currentTempStr = fullXml.split("<temp_f>")[1].split("</temp_f>")[0]
      temperature = float(currentTempStr)
   except:
      pass
   return temperature


################################################################################
# Test Functions
################################################################################
def test():
   while 1:
      readTemp = getTempFromWeb(WEATHER_URL)
      logMsg(str(readTemp))
      time.sleep(6)
     
     
#test()
