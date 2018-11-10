
#Import binanace API
from binance.client import Client
#Import libraries
from datetime import datetime
import pandas as pd

#import modules
from digest import digester
from testAnalyser import testAnalyzer

#Initiate Client connection to Binance
client = Client("", "")

#get data from Binance
coinData = client.get_historical_klines(symbol= 'BTCUSDT', interval= '30m', start_str= '2017.7.17')

#format data into table of Candles
Candles = pd.DataFrame(coinData, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])

#format time data Candles['Open time'] = pd.to_datetime(Candles['Open time'], unit='ms')

#get time data for analysis
time = Candles['Open time']

# type-cast all prices into floats
Candles["Open"] = Candles["Open"].astype(float)
Candles["Close"] = Candles["Close"].astype(float)
Candles["High"] = Candles["High"].astype(float)
Candles["Low"] = Candles["Low"].astype(float)
Candles["Open time"] = Candles["Open time"].astype(float)/1000

#init digester
digest = digester()

#get first price
firstPrice = Candles["Open"][0] 

#set trading fee multiplyer
tradingFee = 1-0.00075 # 0.99925

#init analyzer with first price and trading fee 
analyzer = testAnalyzer(firstPrice,tradingFee )

#start looping throu Candles
for i,Candle0 in Candles.iterrows():

    #take current price
    price = Candle0["Open"]

    #take current time
    timestamp = Candle0["Open time"]

    #get signal from digesting current Candle
    signal = digest.digestCandle(Candle0)

    #Analyze signal
    analyzer.addToAnalysis(signal,price, timestamp)
        

#show analysis
analyzer.analyze(time)

    

    