# Standard
from typing import Callable, Union
import datetime

# Module
import dataprovider

# Site Lib
import pandas as pd
import pandas_ta as ta # Interface for TA-Lib

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

# TODO: Implement multiconditional
class Strategy:
    def __init__(self, name, entry_condition:Callable[[HistoricalMarket], bool], exit_condition:Callable[[HistoricalMarket], bool]):
        self.name = name
        self.entry_condition = entry_condition
        self.exit_condition = exit_condition

    def entry(self, market:HistoricalMarket) -> bool:
        return self.entry_condition(market)

    def close(self, market:HistoricalMarket) -> bool:
        return self.exit_condition(market)
    
class Trade:
    """
        Ongoing Trade
    """
    def __init__(self, entry_date:datetime.datetime, entry_price:float, condition:Strategy):
        self.date = entry_date
        self.price = entry_price
        self.condition = condition
        self.closed = False

    def exit(self, market:HistoricalMarket) -> bool:
        return self.condition.close(market)

    def close(self, exit_date:datetime.datetime, exit_price:float):
        self.closed = True
        self.exit_date = exit_date
        self.exit_price = exit_price

class Backtest:
    runningtrade:list[Trade] = []
    trade_list:list[Trade] = []
    def __init__(self, stock:str):
        self.stock = stock
        self.market = HistoricalMarket(stock)

    def run(self, conditions:list[Strategy]):
        for days in range(len(self.market.full_data)):
            # Get next market data
            self.market.next()

            # Entry Points
            for condition in conditions:
                if condition.entry(self.market):
                    self.runningtrade.append(Trade(self.market.data.index[-1], self.market.data.iloc[-1]['Close'], condition))

            # Exit Points
            for trade in self.runningtrade:
                if trade.exit(self.market):
                    trade.close(self.market.data.index[-1], self.market.data.iloc[-1]['Close'])
                    self.trade_list.append(trade)
                    self.runningtrade.remove(trade)

def entry(market:HistoricalMarket) -> bool:
    market.full_data['CDL_ENGULFING'] = market.full_data.ta.cdl_pattern(name="engulfing")
    print(market.full_data[market.full_data['CDL_ENGULFING'] == -100])
    # print(market.full_data[market.full_data['Close'].isnull()])
    return False

def exit(market:HistoricalMarket) -> bool:
    return False

if __name__ == '__main__':
    market = HistoricalMarket('TLKM')
    entry(market)
    # myStrategy = Strategy(
    #     name = 'CandleStrategy',
    #     entry_condition = entry,
    #     exit_condition = exit
    # )
    # def entry(x:HistoricalMarket):
    #     return x.data.iloc[-1]['Close'] > x.data.iloc[-1]['Open']
    # stragegy = [
    #     Strategy('basic', func, func)
    # ]
    # test = Backtest('TLKM')
    # test.run(stragegy)
