#Import binanace API
from binance.client import Client
#Import libraries
from datetime import datetime
import time
import pandas as pd
import math


class dataProvider:

    #class variables
    pair = ""
    interval = ""
    intervalInSeconds = 0

    #return candle frontRun seconds before it closes
    frontRun = 0

    # integer time at which Candle closes
    lastCandleOpen = 0

    client = None


    def getCurrentCandle(self):

        client = self.client

        #get the time from 4 candles ago in milliseconds (2-3 candles might work as well)
        startTime = int( time.time() - (4 * self.intervalInSeconds) ) * 1000
        
        #get data
        data = client.get_historical_klines(symbol = self.pair, interval = self.interval, start_str = startTime)
        #format data
        data_df = pd.DataFrame(data, columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])

        #typecast to float
        data_df["Open"] = data_df["Open"].astype(float)
        data_df["Close"] = data_df["Close"].astype(float)
        data_df["High"] = data_df["High"].astype(float)
        data_df["Low"] = data_df["Low"].astype(float)
        data_df["Open time"] = data_df["Open time"].astype(float)

        #get index of last(current) candle
        lastIndex = (data_df["Open time"].count())-1

        #return last(current) candle
        return data_df.ix[lastIndex]

    def getLastPrice(self):

        lastPrice = self.client.get_ticker(symbol = self.pair)["lastPrice"]

        return lastPrice



    def monitorMarket(self):

        #wait 1 sec 

        time.sleep(0.2)

        lastPrice = self.getLastPrice()

        
        #get and return current candle
        currentCandle = self.getCurrentCandle()

        #if current candle is closing
        if currentCandle["Open time"]!=self.lastCandleOpen:
            self.lastCandleOpen = currentCandle["Open time"]
            return currentCandle, lastPrice
        else:
            #if no new candle return empty series
            self.lastCandleOpen = currentCandle["Open time"]
            return pd.Series([]), lastPrice



    def __init__(self, _client,  _pair,  _interval, _frontRun):

        print "initiating Candle Provider"

        self.client = _client
        self.interval = _interval
        self.pair = _pair 
        self.frontRun = _frontRun

        #translate interval into intervalInSeconds
        if self.interval == "1m":
            self.intervalInSeconds = 60
        elif self.interval == "3m":
            self.intervalInSeconds = 180
        elif self.interval == "5m":
            self.intervalInSeconds = 300
        elif self.interval == "10m":
            self.intervalInSeconds = 600
        elif self.interval == "15m":
            self.intervalInSeconds = 900
        elif self.interval == "30m":
            self.intervalInSeconds = 1800
        elif self.interval == "1h":
            self.intervalInSeconds = 3600
        elif self.interval == "2h":
            self.intervalInSeconds = 7200
        elif self.interval == "4h":
            self.intervalInSeconds = 14400
        elif self.interval == "6h":
            self.intervalInSeconds = 21600
        elif self.interval == "8h":
            self.intervalInSeconds = 28800
        elif self.interval == "12h":
            self.intervalInSeconds = 43200
        elif self.interval == "1d":
            self.intervalInSeconds = 86400
        elif self.interval == "3d":
            self.intervalInSeconds = 259200

        #init current candle
        currCandle = self.getCurrentCandle()

        self.nextCandleOpens = float(currCandle["Open time"] / 1000) + self.intervalInSeconds
        
        print "initiated Candle Provider"
        

    





    