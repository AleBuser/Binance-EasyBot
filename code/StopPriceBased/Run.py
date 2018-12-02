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
interval  = "15m"

#init the libraries

# last param:  True is Production, False is TEST 
Strategy = digester(client, pair, interval, True) 

Trader = binanceTrader(client, pair, Strategy.Trend )
#last param: return Candles 3 seconds before candele close
Connection = dataProvider(client, pair, interval, 1)

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

            print "Order to "+ Signal +" be placed at: " + str(Stop)
            order = Trader.tradeSignal(Signal,Stop)

            lastCandleOpenTime = newCandle["Open time"]
        else:
            print "blocket a duble Candle"
            







    
        


    
