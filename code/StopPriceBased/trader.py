import time
import sys
import math
import datetime, getopt
import pandas as pd
from datetime import datetime
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


    def cancelLastOrder(self):
        #get order ID
            lastOrderID = self.lastOrder["orderId"]

            #get information about order
            lastOrder = self.client.get_order(symbol = self.pair,orderId = lastOrderID)

            #from information get status
            lastOrderStatus = lastOrder["status"]

            #if order wasnt Filled
            if lastOrderStatus != "FILLED":

                #cancel the order
                try:
                    res = self.client.cancel_order(symbol = self.pair, orderId = lastOrderID)
                except:
                    print "--NO---OPEN---ORDER---FOUND"
                
                self.lastOrder = None

                print "--CANCELED-----ORDER-----"

                return True
            else:

                self.lastOrder = None

                print "--ORDER-----FILLED-----"

                return False


    def checkFounds(self,_side,_price):

        if _side == "BUY":

            _balance = float(self.client.get_asset_balance(asset = self.quote)["free"])

            if _price == -1:
                _price = float(self.client.get_ticker(symbol = self.pair)["lastPrice"])

            _quantity = format(round(_balance / _price, self.roundToStep) - self.stepSize * 10, '.6f')

            if float(_quantity) >= float(self.minQty*10):
                print "---HAS--FUNDS------TO---BUY: "+ str(_quantity)
                return _quantity
            else:
                print "----HAS---NO---FUNDS---TO---BUY"
                Funds = self.checkFounds("SELL",-1)
                self.marketSell(Funds)
                return -1

        else:
            _balance = float(self.client.get_asset_balance(asset = self.base)["free"])

            _quantity = format(round(_balance, self.roundToStep) - self.stepSize * 10 , '.6f')

            if float(_quantity) >= float(self.minQty*10):
                print "----HAS---FUNDS---TO---SELL: "+ str(_quantity)
                return _quantity
            else:
                print "----HAS---NO---FUNDS---TO---SELL"
                Funds = self.checkFounds("BUY",-1)
                self.marketBuy(Funds)
                return -1


    def marketBuy(self, _quantity):

        lastPrice = float(self.client.get_ticker(symbol = self.pair)["lastPrice"])
        try:
            order = self.client.order_limit_buy(
                    symbol=self.pair,
                    quantity=_quantity,
                    price=lastPrice)

            print "------NEW---MARKET_BUY---ORDER SET AT--- " + str(lastPrice) + "----------  " + str(datetime.utcnow() )

        except:
            print "----FAILED---TO---MAKE---ORDER----"
            order = None

        self.lastOrder = order 
        #return order
        return order


    def marketSell(self, _quantity):

        lastPrice = float(self.client.get_ticker(symbol = self.pair)["lastPrice"])
        try:
            order = self.client.order_limit_sell(
                    symbol=self.pair,
                    quantity=_quantity,
                    price=lastPrice)

            print "------NEW---MARKET_SELL---ORDER SET AT--- " + str(lastPrice) + "----------  " + str(datetime.utcnow() )
        except:
            print "----FAILED---TO---MAKE---ORDER----"
            order = None

        self.lastOrder = order 
        #return order
        return order



    def executeMarketOrder(self,_side):

        if self.lastOrder != None:

            self.cancelLastOrder()

        if _side == "BUY":
            hasFounds = self.checkFounds(_side,-1)
            if hasFounds != -1 :
                return self.marketBuy(hasFounds)
                
        else:
            hasFounds = self.checkFounds(_side,-1)
            if hasFounds != -1 :
                return self.marketSell(hasFounds)



    def setBuyStop(self, _stopPrice,_quantity):

        _price = float(_stopPrice)
        _price = round(_price, self.roundToTick)

        try:
            order = self.client.create_order(
                    symbol=self.pair,
                    side="BUY",
                    type="STOP_LOSS_LIMIT",
                    timeInForce = "GTC",
                    quantity=_quantity,
                    price = _price,
                    stopPrice=_price
                )
            
            print "----NEW "+ "STOP_BUY" + " ORDER SET AT: " + str(_price) + "----------  " + str(datetime.utcnow() )
        except:
            print "----FAILED---TO---MAKE---ORDER----"
            order = None
        #save order to use in next round
        self.lastOrder = order 
        #return order
        return order
  

    def setSellStop(self, _stopPrice, _quantity):

        _price = float(_stopPrice)
        _price = round(_price, self.roundToTick)
        try:
            order = self.client.create_order(
                    symbol=self.pair,
                    side="SELL",
                    type="STOP_LOSS_LIMIT",
                    timeInForce = "GTC",
                    quantity=_quantity,
                    price = _price,
                    stopPrice=_price
                )

            print "----NEW "+ "STOP_SELL" + " ORDER SET AT: " + str(_price) + "----------  " + str(datetime.utcnow() )
        except:
            print "----FAILED---TO---MAKE---ORDER----"
            order = None
        #save order to use in next round
        self.lastOrder = order 
        #return order
        return order



    def tradeSignal(self, _signal, _stopPrice):

        if self.lastOrder != None:
            self.cancelLastOrder()

        Funds = self.checkFounds(_signal, _stopPrice)

        #get signal and create orders
        if _signal == "BUY":
            if Funds != -1:
                print self.setBuyStop(_stopPrice, Funds)
            

        if _signal == "SELL":
            if Funds != -1:
                print self.setSellStop(_stopPrice, Funds)







    def __init__(self, _client, _pair, _initialTrend):

        print "initiating Trader"

        self.pair = _pair
        self.client = _client

        #get stepSize of given pair
        self.stepSize = float(self.client.get_symbol_info(_pair)["filters"][1]["stepSize"])
        print _pair + " StepSize: " + str(self.stepSize)

        #get tickSize of given pair
        self.tickSize = float(self.client.get_symbol_info(_pair)["filters"][0]["tickSize"])
        print _pair + " TickSize: " + str(self.tickSize)

        #get minimum quantity
        self.minQty = float(self.client.get_symbol_info(_pair)["filters"][1]["minQty"])
        print _pair + " Minimum quantity: " + str(self.minQty)

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

        allOrders = _client.get_open_orders(symbol = _pair)

        if len(allOrders) != 0:
            print   "--FOUND--OPEN--ORDER--"
            self.lastOrder = allOrders[0]
            self.cancelLastOrder()

        if _initialTrend == "UP":
            print self.executeMarketOrder("BUY")
        else:
            print self.executeMarketOrder("SELL")


        print "initiated Trader"
