import time
import sys
import math
import datetime, getopt
import pandas as pd
from binance.client import Client


class binanceTrader:

    client = None

    pair = ""

    # in "BTCUSDT" quote=USDT base=BTC
    quote = ""
    base = ""

    #binance only handles a given amount of digits, need to rount to that 
    roundTo = 0
    # each pair has a different stepSize 
    stepSize = 0 

    def __init__(self, _client, _pair):

        print "initiating Trader"

        self.pair = _pair
        self.client = _client

        #get stepSize of given pair
        self.stepSize = float(self.client.get_symbol_info(_pair)["filters"][1]["stepSize"])

        #get how many digits are supported from stepSize
        for x in xrange(1,9):
            if self.stepSize == 1.0 / (10 ** x):
                self.roundTo =  x
                break;
        
        #get base/quote assets
        self.quote = self.client.get_symbol_info(_pair)["quoteAsset"]
        self.base = self.client.get_symbol_info(_pair)["baseAsset"]

        print "initiated Trader"



    def makeTradeBuy(self):

        #get last price and current balance of quote asset
        _price = float(self.client.get_ticker(symbol = self.pair)["lastPrice"])
        _balance = float(self.client.get_asset_balance(asset = self.quote)["free"])

        #round and than subtract to avoid rounding to value higher than balance, margin can be adjusted
        #NOTE: _quantity is amount of base asset to be bought with quote asset
        _quantity =  round(_balance / _price, self.roundTo) - self.stepSize * 2 

        #create order to buy entire balance 
        order = self.client.order_limit_buy(
            symbol = self.pair,
            quantity = _quantity,
            price = _price
        )
        #print and return order 
        print order
        return order 


    def makeTradeSell(self):

        #get last price and current balance of base asset
        _price = float(self.client.get_ticker(symbol = self.pair)["lastPrice"])
        _balance = float(self.client.get_asset_balance(asset = self.base)["free"])

        #round and than subtract to avoid rounding to value higher than balance
        #NOTE: _quantity is amount of base asset to be sold
        _quantity =  round(_balance, self.roundTo) - self.stepSize * 2 

        #create order to sell entire balance 
        order = self.client.order_limit_sell(
            symbol = self.pair,
            quantity = _quantity,
            price = _price
        )
        #print and return order
        print order
        return order 


    def tradeSignal(self, _signal):

        #get signal and create orders
        if _signal == "BUY":
            _order = self.makeTradeBuy()

        if _signal == "SELL":
            _order = self.makeTradeSell()



