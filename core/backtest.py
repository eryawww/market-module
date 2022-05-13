# Standard
import os
import sys
from typing import Callable, Union
import datetime

sys.path.append(os.path.dirname(__file__))
# Module
import dataprovider

# Site Lib
import pandas as pd
import pandas_ta as ta # Interface for TA-Lib
import numpy as np

# TODO: Implement multitimeframe
class HistoricalMarket:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.full_data:pd.DataFrame = dataprovider.get_market_data(symbol)
        self.data = pd.DataFrame(columns=self.full_data.columns)
        
    def next(self) -> pd.DataFrame:
        '''
            Get the next data and append it in self.data
        '''
        try:
            self.data = pd.concat([self.data, self.full_data.iloc[self.data.shape[0]].to_frame().T])
        except IndexError as e:
            raise IndexError("No more data")

        return self.data

    def get(self, lookback:int) -> Union[pd.DataFrame, None]:
        '''
            Get the data in lookback days
            Return None in case of required more data
        '''
        try:
            return self.data.iloc[-lookback:]
        except IndexError:
            return None

#TODO: Make stub since this is dynamic
class Strategy:
    """
        entry_condition: function(HistoricalMarket) return bool, whether we should buy or not
        exit_condition: function(HistoricalMarket) return bool, whether we should sell or not
        you can use multi stop_loss or take_profit by adding new variable to the kwargs and check that variable using first parameter in the entry_condition/exit_condition
        parameter hint is None because we have to use python dynamicity in this case
    """
    def __init__(self, name, entry_condition:Callable[[HistoricalMarket], bool], exit_condition:Callable[[HistoricalMarket], bool], **kwargs):
        self.name = name
        self.entry_condition = entry_condition
        self.exit_condition = exit_condition
        self.__dict__.update(kwargs)

    def entry(self, market:HistoricalMarket) -> bool:
        return self.entry_condition(market)

    def exit(self, market:HistoricalMarket) -> bool:
        return self.exit_condition(market)

class Trade:
    """
        Ongoing Trade
        Entry is at one point of time
        Exit is at multiple point of time (list[datetime], list[float])
    """
    exit_date = []
    exit_price = []
    exit_amount = []
    def __init__(self, amount:float):
        self.initial_amount = amount
        self.amount_left = amount
        self.closed = False

    def _post_init(self, entry_date:datetime.datetime, entry_price:float, strategy:Strategy):
        self.entry_price = entry_price
        self.entry_date = entry_date
        self.strategy = strategy

    def exit(self, market:HistoricalMarket) -> bool:
        return self.strategy.exit(market)

    def close(self, exit_date:datetime.datetime, exit_price:float, amount:float, closed:bool):
        self.exit_date.append(exit_date)
        self.exit_price.append(exit_price)
        self.exit_amount.append(amount)
        self.amount_left -= amount
        self.closed = closed

#TODO: Implement Fee
#TODO: Implement trade_graph for clear entry exit
class Management:
    """
        All a trade opportunity will be send here
        entry_confirmation: function(mgt:Management, price:float, strategy) return Trade or None
        exit_confirmation: function(mgt:Management, price:float, trade:Trade) return amount, 0 for cancel -1 for full sell from this trade
        mgt is used to check initial balance or current balance
    """
    running_trade:list[Trade] = []
    done_trade:list[Trade] = []
    def __init__(self, initial_balance:float, entry_confirmation:Callable[[None, float, Strategy], Trade], exit_confirmation:Callable[[None, float, Trade], float], **kwargs):
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.entry_confirmation = entry_confirmation
        self.exit_confirmation = exit_confirmation
        self.__dict__.update(kwargs)

    def buy(self, date:datetime.datetime, price:float, strategy:Strategy):
        trade = self.entry_confirmation(self, price, strategy)
        if trade is None:
            return

        trade._post_init(date, price, strategy)
        assert trade.amount_left*price <= self.balance
        self.open_trade(trade)
        self.balance -= trade.amount_left * price

    def sell(self, date:datetime.datetime, price:float, trade:Trade):
        amount = self.exit_confirmation(self, price, trade)
        if amount == 0:
            return
        elif amount == -1:
            amount = trade.amount_left

        assert amount <= trade.amount_left
        self.close_trade(trade, amount, date, price)
        self.balance += amount * price

    def print_stats(self):
        print('------------------ BALANCE ------------------')
        print('Initial Balance\t: ', self.initial_balance)
        print('Current Balance\t: ', self.balance, 'ROI: ', (self.balance-self.initial_balance)/self.initial_balance*100, '%')
        print('Change \t: ', self.balance-self.initial_balance)
        print('------------------ TRADE ------------------')
        print('Open Trade\t: ', len(self.running_trade))
        print('Done Trade\t: ', len(self.done_trade))
        print('------------------ DONE TRADE ------------------')
        for trade in self.done_trade:
            print('Date\t: ', trade.entry_date)
            print('Entry Price\t: ', trade.entry_price)
            print('Amount\t: ', trade.initial_amount)
            entry_total = trade.entry_price*trade.initial_amount
            print('ROI\t: ', (entry_total-(trade.initial_amount-trade.amount_left)*trade.entry_price)/entry_total*100, '%')
            print('------------------')
    
    def open_trade(self, trade:Trade):
        self.running_trade.append(trade)

    def close_trade(self, trade:Trade, amount:float, exit_date:datetime.datetime, exit_price:float):
        # In case precision error
        if amount == -1:
            amount = trade.amount_left
        if trade.amount_left-amount <= 0.0000000001:
            trade.close(exit_date, exit_price, amount, True)
            self.running_trade.remove(trade)
            self.done_trade.append(trade)
        else:
            trade.close(exit_date, exit_price, amount, False)

#TODO ADD LIMIT ORDER
#TODO ADD MULTI SYMBOLS
class Backtest:
    management = Management(
        initial_balance = 1_000_000_000,
        entry_confirmation = lambda a, b, c: Trade(1),
        exit_confirmation = lambda a, b, c: -1,
    )
    def __init__(self, stock:str, management:Management=management):
        self.stock = stock
        self.market = HistoricalMarket(stock)
        self.management = management

    def print_stats(self):
        self.management.print_stats()

    def run(self, strategies:list[Strategy]):
        for days in range(len(self.market.full_data)):
            # Get next market data
            self.market.next()
            price = self.market.data.iloc[-1]['Close']
            date = self.market.data.index[-1]

            # Entry Points
            for strategy in strategies:
                if strategy.entry(self.market):
                    self.management.buy(date, price, strategy)

            # Exit Points
            for trade in self.management.running_trade:
                if trade.exit(self.market):
                    self.management.sell(date, price, trade)