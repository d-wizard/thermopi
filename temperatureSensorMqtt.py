
#!/usr/bin/python3

import os
import time
import argparse
import paho.mqtt.publish as publish

PATH_TO_SENSOR = ""

def temp_raw():
   global PATH_TO_SENSOR
   temp_sensor = PATH_TO_SENSOR #'/sys/bus/w1/devices/28-xxxxxxxxxxxx/w1_slave'
   f = open(temp_sensor, 'r')
   lines = f.readlines()
   f.close()
   return lines

def read_temp():
   lines = temp_raw()
   while lines[0].strip()[-3:] != 'YES':
      time.sleep(0.2)
      lines = temp_raw()
   
   temp_output = lines[1].find('t=')
   
   if temp_output != -1:
      temp_string = lines[1].strip()[temp_output+2:]
      temp_c = float(temp_string) / 1000.0
      temp_f = temp_c * 9.0 / 5.0 + 32.0
      return temp_c, temp_f

def findTempSensor(serialNum = None):
   pathToSensor = ""
   sensorBasePath = '/sys/bus/w1/devices/'
   sensorPrefix = '28-'
   sensorFile = 'w1_slave'

   if serialNum != None:
      tryPath = os.path.join(sensorBasePath, sensorPrefix+serialNum, sensorFile)
      if os.path.isfile(tryPath):
         pathToSensor = tryPath

   if pathToSensor == "" and os.path.isdir(sensorBasePath):
      sensors = os.listdir(sensorBasePath)
      for sensor in sensors:
         try:
            if sensor[:len(sensorPrefix)] == sensorPrefix and os.path.isfile(os.path.join(sensorBasePath, sensor, sensorFile)):
               pathToSensor = os.path.join(sensorBasePath, sensor, sensorFile)
         except:
            pass

   return pathToSensor


def temperatureSensor_init(serialNum = None):
   global PATH_TO_SENSOR
   PATH_TO_SENSOR = findTempSensor(serialNum)
   os.system('modprobe w1-gpio')
   os.system('modprobe w1-therm')

def temperatureSensor_getFahrenheit():
   temperature = None
   try:
      dummy, temperature = read_temp()
   except:
      pass
   return temperature

def temperatureSensor_getCelsius():
   temperature = None
   try:
      temperature, dummy = read_temp()
   except:
      pass
   return temperature



def temperatureSensor_debugTest():
   temperatureSensor_init()
   while True:
      print(read_temp())
      print(temperatureSensor_getFahrenheit())
      print(temperatureSensor_getCelsius())
      time.sleep(1)
      
# Main start
if __name__== "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument("-b", type=str, action="store", dest="broker", help="Broker IP Addr", default="127.0.0.1")
   parser.add_argument("-p", type=int, action="store", dest="port", help="Broker Port", default=8883)
   parser.add_argument("-t", type=str, action="store", dest="topic", help="Topic", default=None)
   parser.add_argument("-u", type=str, action="store", dest="username", help="Auth User Name", default=None)
   parser.add_argument("-w", type=str, action="store", dest="password", help="Auth Password", default=None)
   parser.add_argument("-o", type=int, action="store", dest="pollPeriod", help="How often to poll the sensor in seconds", default=30)
   args = parser.parse_args()

   if args.topic == None:
      print("Topic needs to be specified")
      exit(0)

   temperatureSensor_init()

   while True:
      try:
         publish.single(args.topic, str(temperatureSensor_getFahrenheit()), hostname=args.broker, port=args.port)
      except:
         pass
      time.sleep(args.pollPeriod if args.pollPeriod > 0 else 30)
