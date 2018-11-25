#Import binanace API
from binance.client import Client
#Import libraries
from datetime import datetime
import time
import pandas as pd
import sys

#add all startegies to importable
sys.path.insert(0, 'strategies')

from digest import digester
from trader import binanceTrader
from CandleProvider import dataProvider

#Initiate Client connection to Binance
client = Client("KEY", "KEY")

#select trading pair and time from whitch to get data
pair  = "BTCUSDT"
interval  = "5m"

#init the libraries

# last param:  True is Production, False is TEST 
Strategy = digester(client, pair, interval, True) 

Trader = binanceTrader(client, pair)
#last param: return Candles 3 seconds before candele close
Connection = dataProvider(client, pair, interval, 2)

Stop = 0

Trend = "UP"

lastCandleOpenTime = 0

#main loop
while True:


    #check for new candle an gets last seconds price
    newCandle, lastPrice = Connection.monitorMarket()

    lastPrice = float(lastPrice)

    #if a new candle closed
    if(newCandle.empty == False):
        if newCandle["Open time"] != lastCandleOpenTime:

            #give new candle to digester to analyze 
            Stop, Signal = Strategy.digestCandle(newCandle)
            Stop = float(Stop)

            Trader.tradeSignal(Signal,Stop)

            # print a digested Signala and time 
            print "---------- NEW "+ Signal + " ORDER SET AT: " + str(Stop) + "----------  " + str(datetime.utcnow() ) 
            #print "---------- TREND IS " + str(Trend) + "----------  "
            lastCandleOpenTime = newCandle["Open time"]
        else:
            print "blocket a duble Candle"
            







    
        


    
