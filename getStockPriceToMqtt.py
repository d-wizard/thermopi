import os
import time
from urllib.request import urlopen
from datetime import datetime
import argparse
import yfinance as yf
import paho.mqtt.publish as publish


################################################################################
# API Functions
################################################################################
def getCurrentStockPrice(stock):
   stockPrice = None
   try:
      ticker = yf.Ticker(stock)
      stockPrice = float(ticker.info['regularMarketPrice'])
   except:
      pass
   return stockPrice

# Main start
if __name__== "__main__":
   parser = argparse.ArgumentParser()
   parser.add_argument("-b", type=str, action="store", dest="broker", help="Broker IP Addr", default="127.0.0.1")
   parser.add_argument("-p", type=int, action="store", dest="port", help="Broker Port", default=8883)
   parser.add_argument("-T", type=str, action="store", dest="ticker", help="Stock Ticker", default=None)
   parser.add_argument("-t", type=str, action="store", dest="topic", help="Topic", default=None)
   parser.add_argument("-u", type=str, action="store", dest="username", help="Auth User Name", default=None)
   parser.add_argument("-w", type=str, action="store", dest="password", help="Auth Password", default=None)
   parser.add_argument("-o", type=int, action="store", dest="pollPeriod", help="How often to poll the sensor in seconds", default=300)
   args = parser.parse_args()

   if args.ticker == None:
      print("Stock Ticker needs to be specified")
      exit(0)

   if args.topic == None:
      args.topic = "stock/" + args.ticker

   while True:
      try:
         stockPrice = getCurrentStockPrice(args.ticker)
         if stockPrice != None:
            # print(str(stockPrice))
            publish.single(args.topic, str(stockPrice), hostname=args.broker, port=args.port)
      except:
         pass
      time.sleep(args.pollPeriod if args.pollPeriod > 0 else 300)
