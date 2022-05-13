# Standard
from typing import Callable, Union
import datetime

# Module
import core.dataprovider
from core.core import Strategy, HistoricalMarket, Backtest, Trade

# Site Lib
import pandas as pd
import pandas_ta as ta # Interface for TA-Lib


def entry(market:HistoricalMarket) -> bool:
    # market.full_data['CDL_ENGULFING'] = market.full_data.ta.cdl_pattern(name="engulfing")
    # print(market.full_data[market.full_data['CDL_ENGULFING'] == -100])
    return True

def exit(market:HistoricalMarket) -> bool:
    return True

if __name__ == '__main__':
    market = HistoricalMarket('TLKM')
    myStrategy = Strategy(
        name = 'CandleStrategy',
        entry_condition = entry,
        exit_condition = exit
    )
    test = Backtest('TLKM')
    test.run([myStrategy])
    test.print_stats()