#Import libraries
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

#initiate class
class testAnalyzer():

    #initiate global class variables
    fee = 0
    StartingCapital = 0
    FirstPrice = 0

    Capital = 0
    Crypto = 0
    
    capitalBefore = 0

    lastPrice = 0
    
    highestGain = 0;
    highestLost = 0;

    tradesGood = [];
    tradesBad = [];

    balances = []
    prices = []

    def __init__(self,_capital,_fee):

        self.fee = _fee

        self.StartingCapital = _capital

        self.Capital = _capital
        self.capitalBefore = 0

        self.lastPrice = 0
        self.FirstPrice = 0

        self.Crypto = 0

        self.highestGain=0;
        self.highestLost=0;

        self.tradesGood=[];
        self.tradesBad=[];

        self.balances = pd.DataFrame(columns=['Capital'])
        self.prices = pd.DataFrame(columns=['Price'])

    def addToAnalysis(self,_signal,_price, _time):

        if self.FirstPrice == 0:
            self.FirstPrice = _price
        
        self.lastPrice = _price

        self.balances = self.balances.append({'Capital':max(self.Capital, self.Crypto * _price)}, ignore_index=True)
        self.prices = self.prices.append({'Price':_price}, ignore_index=True)

        if _signal == "BUY":

            self.capitalBefore = self.Capital

            self.Crypto = self.Capital / _price 
            self.Crypto = self.Crypto * self.fee

            self.Capital = 0;

            print "::::::::::::::::::::::::::::::::::::BUY " + str(_price) + " " + str(datetime.utcfromtimestamp(_time).strftime('%Y-%m-%d %H:%M:%S'))

        if _signal == "SELL":

            self.Capital = self.Crypto * _price
            self.Capital = self.Capital * self.fee

            print "::::::::::::::::::::::::::::::::::::SELL " + str(_price)  + " " + str(datetime.utcfromtimestamp(_time).strftime('%Y-%m-%d %H:%M:%S'))

            #check if new best/worst trade
            if (((self.Capital / self.capitalBefore) * 100) - 100) > self.highestGain:
                self.highestGain = ((self.Capital / self.capitalBefore) * 100) - 100
            if (((self.Capital / self.capitalBefore) * 100) - 100)  < self.highestLost:
                self.highestLost = ((self.Capital / self.capitalBefore) * 100) - 100

            print "Profit on trade: " +  str(((self.Capital / self.capitalBefore)*100)-100) + "%"

            if(self.Capital - self.capitalBefore >= 0) :
                self.tradesGood.append((( self.Capital / self.capitalBefore) * 100) - 100);
            else:
                self.tradesBad.append(((self.Capital / self.capitalBefore) * 100) - 100)


    def analyze(self, _time):

        _price = self.lastPrice

        print "Starts with " + str(self.StartingCapital) + ", ends with: " + str(_price * self.Crypto)
        print "Buy-and-Hold strategy ends with: "+str(_price * (self.StartingCapital / self.FirstPrice));
        print "Profit :"+str((((_price*self.Crypto) / self.StartingCapital)*100)-100) + "%"
        print "Compared against buy-and-hold :"+ str(((_price * self.Crypto)/(_price * (self.StartingCapital / self.FirstPrice))) * 100)+ "%"
        print "best trade :"+str(self.highestGain)  + "%"
        print "worst trade :" + str(self.highestLost) + "%"

        summ=0
        for l in self.tradesGood:
            summ+=l
        print "Avarage good trade :"+ str(summ/len(self.tradesGood)) + "%"
        print "Number of good trades :"+ str(len(self.tradesGood)) 
        summ=0
        for k in self.tradesBad:
            summ+=k
        print "Avarage bad trade :"+ str(summ/len(self.tradesBad)) + "%"
        print "Number of bad trades :"+ str(len(self.tradesBad))



        #plot everything
        plt.plot(_time,self.prices,'b',label="Price BTC")
        plt.plot(_time,self.balances,'r',label="Capital")
        plt.legend()
        plt.grid(True)
        plt.show()



