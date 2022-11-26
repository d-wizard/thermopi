import os
import time
from urllib.request import urlopen
from datetime import datetime
import argparse
import paho.mqtt.publish as publish

WEATHER_URL = "http://w1.weather.gov/xml/current_obs/display.php?stid=KCID"


################################################################################
# API Functions
################################################################################
def getTempFromWeb(url = WEATHER_URL):
   temperature = None
   try:
      webURL = urlopen(WEATHER_URL)
      fullXml = webURL.read().decode('utf-8')
      currentTempStr = fullXml.split("<temp_f>")[1].split("</temp_f>")[0]
      temperature = float(currentTempStr)
   except:
      pass
   return temperature

# Main start
if __name__== "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument("-b", type=str, action="store", dest="broker", help="Broker IP Addr", default="127.0.0.1")
   parser.add_argument("-p", type=int, action="store", dest="port", help="Broker Port", default=8883)
   parser.add_argument("-t", type=str, action="store", dest="topic", help="Topic", default=None)
   parser.add_argument("-u", type=str, action="store", dest="username", help="Auth User Name", default=None)
   parser.add_argument("-w", type=str, action="store", dest="password", help="Auth Password", default=None)
   parser.add_argument("-o", type=int, action="store", dest="pollPeriod", help="How often to poll the sensor in seconds", default=300)
   args = parser.parse_args()

   if args.topic == None:
      print("Topic needs to be specified")
      exit(0)

   while True:
      try:
         tempF = getTempFromWeb()
         if tempF != None:
            publish.single(args.topic, str(tempF), hostname=args.broker, port=args.port)
      except:
         pass
      time.sleep(args.pollPeriod if args.pollPeriod > 0 else 300)
