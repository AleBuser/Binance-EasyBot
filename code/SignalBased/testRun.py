
#Import binanace API
from binance.client import Client
#Import libraries
from datetime import datetime
import pandas as pd
import sys

#add all startegies to importable
sys.path.insert(0, 'strategies')

#import modules
from digest import digester
from testAnalyser import testAnalyzer

#Initiate Client connection to Binance
client = Client("", "")

#chose trading pair, interval and testing start
pair = 'BTCUSDT'
interval = '1d'
analyzeDataFrom = "2017.07.17"

#get data from Binance
print "initiating...."
coinData = client.get_historical_klines(symbol = pair , interval = interval, start_str = analyzeDataFrom)#, end_str= "2018.8.20")

#format data into table of Candles
Candles = pd.DataFrame(coinData, columns = ['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])

#format time data  into new coloumn
Candles['Time series'] = pd.to_datetime(Candles['Open time'], unit='ms')

#get time data for analysis
time = Candles['Time series']

# type-cast all prices into floats
Candles["Open"] = Candles["Open"].astype(float)
Candles["Close"] = Candles["Close"].astype(float)
Candles["High"] = Candles["High"].astype(float)
Candles["Low"] = Candles["Low"].astype(float)
Candles["Open time"] = Candles["Open time"].astype(float)/1000

#init digester
#last param is: True for Production, False for testing
Strategy = digester(client, pair, interval, False)

#get initial balance from initial price of 1 unit
initialBalance = Candles["Open"][0] 

#set trading fee multiplyer
tradingFee = 1 - 0.00075 # 0.99925

#init analyzer with first price and trading fee 
analyzer = testAnalyzer(initialBalance,tradingFee, True )

#start looping throu Candles
for i,Candle0 in Candles.iterrows():

    #take current price
    price = Candle0["Close"]

    #take current time
    timestamp = Candle0["Open time"]

    #get signal from digesting current Candle
    signal = Strategy.digestCandle(Candle0)

    #Analyze signal
    analyzer.addToAnalysis(signal, price, timestamp)
        

#show analysis
analyzer.analyze(time)

    

    
