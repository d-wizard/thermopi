import sys
import os
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)) + "/tplink-smartplug")

import time
import json
from datetime import datetime
import tplinkSmartplugLib

def smartPlug_print(printMsg):
   logMsg = '[' + str(datetime.now()) + "] " + printMsg
   print(logMsg)


def smartPlug_sendCmd(ipAddr, cmd):
   retVal = None
   try:
      smartPlugCmdResult = tplinkSmartplugLib.sendCommand(ipAddr, cmd)
      try:
         retVal = json.loads(smartPlugCmdResult)
      except:
         pass
   except:
      pass
   return retVal



def smartPlug_getState(ipAddr):
   state = None
   try:
      resultJson = smartPlug_sendCmd(ipAddr, 'info')
      try:
         relayStateInt = int(resultJson["system"]["get_sysinfo"]["relay_state"])
         if relayStateInt == 1:
            state = True
         elif relayStateInt == 0:
            state = False
      except:
         pass
   except:
      pass
   return state

def smartPlug_onOff(ipAddr, setToOn):
   success = False
   try:
      resultJson = None
      if setToOn:
         resultJson = smartPlug_sendCmd(ipAddr, 'on')
      else:
         resultJson = smartPlug_sendCmd(ipAddr, 'off')

      try:
         if int(resultJson["system"]["set_relay_state"]["err_code"]) == 0:
            success = True
      except:
         pass

   except:
      pass

   return success

# Toggle Smart Plug on / off
def smartPlug_runDebugTest(ipAddr, sleepBetweenTime):
   currentState = smartPlug_getState(ipAddr)
   goodSetState = True
   
   smartPlug_print("Initial SmartPlug State: " + str(currentState))
   
   while currentState != None and goodSetState == True:
      time.sleep(sleepBetweenTime)
      goodSetState = smartPlug_onOff(ipAddr, not currentState)
      smartPlug_print("Setting SmartPlug State: " + str(not currentState))
      time.sleep(sleepBetweenTime)
      currentState = smartPlug_getState(ipAddr) 
      smartPlug_print("Read SmartPlug State   : " + str(currentState))

   smartPlug_print("Final SmartPlug State  : " + str(currentState))

#smartPlug_runDebugTest("192.168.1.xxx", 5)
