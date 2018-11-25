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
    roundToStep = 0
    roundToTick = 0 
    # each pair has a different stepSize and tickSize 
    stepSize = 0 
    tickSize = 0

    lastOrder = None

    def __init__(self, _client, _pair):

        print "initiating Trader"

        self.pair = _pair
        self.client = _client

        #get stepSize of given pair
        self.stepSize = float(self.client.get_symbol_info(_pair)["filters"][1]["stepSize"])

        #get tickSize of given pair
        self.tickSize = float(self.client.get_symbol_info(_pair)["filters"][0]["tickSize"])

        #get how many digits are supported from stepSize
        for x in xrange(1,9):
            if self.stepSize == 1.0 / (10 ** x):
                self.roundToStep =  x
                break;

        #get how many digites are supported for tickSize
        #get how many digits are supported from stepSize
        for x in xrange(1,9):
            if self.tickSize == 1.0 / (10 ** x):
                self.roundToTick =  x
                break;
        
        #get base/quote assets
        self.quote = self.client.get_symbol_info(_pair)["quoteAsset"]
        self.base = self.client.get_symbol_info(_pair)["baseAsset"]

        print "initiated Trader"


    def checkLastOrder(self):

        #if there was an order before (if not first time)
        if self.lastOrder != None:

            #get order ID
            lastOrderID = self.lastOrder["orderId"]

            #get information about order
            lastOrder = self.client.get_order(symbol = self.pair,orderId = lastOrderID)

            #from information get status
            lastOrderStatus = lastOrder["status"]

            #if order wasnt Filled
            if lastOrderStatus != "FILLED":

                #cancel the order
                res = self.client.cancel_order(symbol = self.pair, orderId = lastOrderID)

                print "-----CANCELED-----ORDER-----"






    def makeTradeBuy(self, _stopPrice):

        #checks if last order was filled, canceles it if not
        self.checkLastOrder()

        #get float of price and current balance of quote asset
        _price = float(_stopPrice)
        _balance = float(self.client.get_asset_balance(asset = self.quote)["free"])

        #round and than subtract to avoid rounding to value higher than balance, margin can be adjusted
        #NOTE: _quantity is amount of base asset to be bought with quote asset typecast to string to avoid exponential notation
        _price = round(_price, self.roundToTick)
        _quantity = str(round(_balance / _price, self.roundToStep) - self.stepSize * 2) 

        #create order to buy entire balance order will be created if lastPrice >= stopPrice
        order = self.client.create_order(
            symbol=self.pair,
            side="BUY",
            type="STOP_LOSS_LIMIT",
            timeInForce = "GTC",
            quantity=_quantity,
            price = _price,
            stopPrice=_price
        )
        #print order 
        print order
        #save order to use in next round
        self.lastOrder = order 
        #return order
        return order 


    def makeTradeSell(self, _stopPrice):

        #checks if last order was filled, canceles it if not
        self.checkLastOrder()

        #get float of price and current balance of base asset
        _price = float(_stopPrice)
        _balance = float(self.client.get_asset_balance(asset = self.base)["free"])

        #round and than subtract to avoid rounding to value higher than balance
        #NOTE: _quantity is amount of base asset to be sold
        _price = round(_price, self.roundToTick)
        _quantity = str(round(_balance, self.roundToStep) - self.stepSize * 2 )

        #create order to sell entire balance, order will be created if lastPrice <= stopPrice
        order = self.client.create_order(
            symbol=self.pair,
            side="SELL",
            type="STOP_LOSS_LIMIT",
            timeInForce = "GTC",
            quantity=_quantity,
            price = _price,
            stopPrice=_price
        )
        #print order 
        print order
        #save order to use in next round
        self.lastOrder = order 
        #return order
        return order  


    def tradeSignal(self, _signal, _stopPrice):

        #get signal and create orders
        if _signal == "BUY":
            _order = self.makeTradeBuy(_stopPrice)

        if _signal == "SELL":
            _order = self.makeTradeSell(_stopPrice)



