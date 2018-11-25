#Import binanace API
from binance.client import Client
#Import libraries
from datetime import datetime
import time
import pandas as pd

from digest import digester
from trader import binanceTrader
from CandleProvider import dataProvider

#Initiate Client connection to Binance with API Keys
client = Client("KEY_HERE", "KEY_HERE")

#select trading pair and time from whitch to get data
pair  = "BTCUSDT"
interval  = "1d"

#init the libraries

# last param:  True is Production, False is TEST 
Strategy = digester(client, pair, interval, True) 

Trader = binanceTrader(client, pair)

#last param: return Candles 3 seconds before candele close
Connection = dataProvider(client, pair, interval, 3)


#main loop
while True:

    #check for new candle
    newCandle = Connection.monitorMarket()

    #if a new candle closed
    if(newCandle.empty == False):

        #give new candle to digester to analyze 
        Signal = Strategy.digestCandle(newCandle)

        # print digested Signala and time 
        print "----------" + Signal + "----------  " + str(datetime.utcnow() ) 

        #if signal is BUY or SELL execute trade
        if Signal != "HOLD":
            
            #execute trade
            Trader.tradeSignal(Signal)


    
        


    
