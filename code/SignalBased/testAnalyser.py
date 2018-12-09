#Import libraries
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

#initiate class
class testAnalyzer():

    #initiate global class variables
    fee = 0
    StartingBalance = 0
    FirstPrice = 0

    # in "BTCUSDT" quote=USDT base=BTC
    #amount of quote asset held 
    quoteBalance = 0
    #amount of base asset held
    baseBalance = 0
    
    #balance of quote asset before buy  
    quoteBalanceBefore = 0

    #last price recieved
    lastPrice = 0
    
    highestGain = 0;
    highestLost = 0;

    #amount of positive/negative trades
    tradesGood = [];
    tradesBad = [];

    #asset balances and prices fro plotting
    balances = []
    prices = []

    showProfit = True

    def __init__(self,_capital,_fee, _showProfit, _showCrypto):

        self.fee = _fee

        self.StartingBalance = _capital

        self.quoteBalance = _capital
        self.baseBalance = 0

        self.quoteBalanceBefore = 0

        self.lastPrice = 0
        self.FirstPrice = 0

        self.highestGain=0;
        self.highestLost=0;

        self.tradesGood=[];
        self.tradesBad=[];

        self.showProfit = _showProfit
        self.showCrypto = _showCrypto

        #init series
        self.BaseBalances = pd.DataFrame(columns=['Base'])
        self.QuoteBalances = pd.DataFrame(columns=['Quote'])
        self.prices = pd.DataFrame(columns=['Price'])
        self.ProfitMA = pd.DataFrame(columns=["Profir"])

    def addToAnalysis(self,_signal,_price, _time):

        #store first price
        if self.FirstPrice == 0:
            self.FirstPrice = _price
        
        #store last price 
        self.lastPrice = _price

        Profit = 0 

        #add current Balances to series
        self.QuoteBalances = self.QuoteBalances.append({'Quote':max(self.quoteBalance, self.baseBalance * _price)}, ignore_index=True)
        self.BaseBalances = self.BaseBalances.append({'Base': max(self.baseBalance, self.quoteBalance / _price)}, ignore_index=True)
        self.prices = self.prices.append({'Price':_price}, ignore_index=True)

        #if signal is BUY simulate a buy order 
        if _signal == "BUY":

            #store balance before trade
            self.quoteBalanceBefore = self.quoteBalance

            
            self.baseBalance = self.quoteBalance / _price

            #subtract percentage fee
            self.baseBalance = self.baseBalance * self.fee

            #print signal, price and time
            print "::::::::::::::::::::::::::::::::::::BUY " + str(_price) + " " + str(datetime.fromtimestamp(_time).strftime('%Y-%m-%d %H:%M:%S'))



        #if signal is BUY simulate a sell order and analyize trade performance
        if _signal == "SELL":

            #simulate trade
            self.quoteBalance = self.baseBalance * _price

            #subtract percentage fee
            self.quoteBalance = self.quoteBalance * self.fee

            #print signal, price and time
            print "::::::::::::::::::::::::::::::::::::SELL " + str(_price)  + " " + str(datetime.fromtimestamp(_time).strftime('%Y-%m-%d %H:%M:%S'))

            #check if the percentage of profit is new best/worst, if yes store it as such
            if (((self.quoteBalance / self.quoteBalanceBefore) * 100) - 100) > self.highestGain:
                self.highestGain = ((self.quoteBalance / self.quoteBalanceBefore) * 100) - 100

            if (((self.quoteBalance / self.quoteBalanceBefore) * 100) - 100)  < self.highestLost:
                self.highestLost = ((self.quoteBalance / self.quoteBalanceBefore) * 100) - 100

            #print profit made on this trade
            Profit = ((self.quoteBalance / self.quoteBalanceBefore)*100)-100

            print "Profit on trade: " +  str(Profit) + "%"

            #check if profit is positive or negative and add to list of Good/Bad trades
            if(self.quoteBalance - self.quoteBalanceBefore >= 0) :
                self.tradesGood.append((( self.quoteBalance / self.quoteBalanceBefore) * 100) - 100);
            else:
                self.tradesBad.append(((self.quoteBalance / self.quoteBalanceBefore) * 100) - 100)
        self.ProfitMA = self.ProfitMA.append({'Profit':Profit}, ignore_index=True)


    def analyze(self, _time):

        #get last price recieved
        _price = self.lastPrice

        #print analytics gained by using list of Good/Bad trades, 
        print "Starts with " + str(self.StartingBalance) + ", ends with: " + str(_price * self.baseBalance) + " / " + str(self.baseBalance) 
        print "Buy-and-Hold strategy ends with: " + str(_price * (self.StartingBalance / self.FirstPrice));
        print "Profit :" + str(((( _price * self.baseBalance) / self.StartingBalance)* 100)) + "%"
        print "Net-Profit :" + str(((( _price * self.baseBalance) / self.StartingBalance)* 100)- 100) + "%"
        print "Compared against buy-and-hold :" + str(((_price * self.baseBalance) / (_price * (self.StartingBalance / self.FirstPrice))) * 100)+ "%"
        print "best trade :" + str(self.highestGain)  + "%"
        print "worst trade :" + str(self.highestLost) + "%"

        #compute and return number and average of Good/Bad trades
        summGood=0
        for l in self.tradesGood:
            summGood+=l
        print "Avarage good trade: "+ str(summGood/len(self.tradesGood)) + "%"
        print "Number of good trades: "+ str(len(self.tradesGood)) 
        summBad=0
        for k in self.tradesBad:
            summBad+=k
        print "Avarage bad trade: "+ str(summBad/len(self.tradesBad)) + "%"
        print "Number of bad trades: "+ str(len(self.tradesBad))
        print "Avarage trade: " + str((summBad+summGood) / (len(self.tradesBad) +len(self.tradesGood))) + "%"
        print "Number of Trades: "  + str(len(self.tradesBad) +len(self.tradesGood))




        if self.showProfit == True:

            plt.subplot(211)
            plt.plot(_time,self.prices,'b',label="Asset Price")
            plt.plot(_time,self.QuoteBalances["Quote"],'r',label="Capital")
            plt.plot(_time,self.BaseBalances["Base"],'g',label="Crypto")
            plt.legend()

            plt.grid(True)
            plt.subplot(212)
            plt.plot(_time,self.ProfitMA,'y',label="% Profit")
            plt.legend()
            plt.grid(True)

        else: 
            fig, ax1 = plt.subplots()

            color = 'tab:red'
            ax1.set_xlabel('time (s)')
            ax1.plot(_time,self.prices,'b',label="Asset Price")
            ax1.plot(_time,self.QuoteBalances["Quote"],'r',label="Capital")
            ax1.tick_params(axis='y', labelcolor=color)
            ax1.legend()

            if self.showCrypto == True:
                ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

                color = 'tab:green'
                ax2.plot(_time,self.BaseBalances["Base"],'g',label="Crypto")
                ax2.tick_params(axis='y', labelcolor=color)
                ax2.legend()
                fig.tight_layout()  # otherwise the right y-label is slightly clipped
        
        plt.show()




