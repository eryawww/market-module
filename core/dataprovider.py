import os
import pandas as pd
import yfinance

data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
index_path = os.path.join(data_path, 'index')

# TODO: Use dynamic index
# Using index name from yfinance
def get_market_data(stock:str) -> pd.DataFrame:
    """
        Get the data for the stock
        Ex: get_data(stock = TLKM)
    """
    stock += '.csv'
    def find_source(x):
        for dir in os.listdir(x):
            if os.path.isdir(os.path.join(x, dir)):
                nw = find_source(os.path.join(x, dir))
                if nw is not None:
                    return nw
            else:
                if dir == stock:
                    return os.path.join(x, dir)
        return None
    data_source = find_source(data_path)
    if data_source is None:
        raise FileNotFoundError(f"Could not find data for {stock}")
    else:
        data = pd.read_csv(data_source, index_col=0)
        return verify_data(data)

def verify_data(data:pd.DataFrame) -> pd.DataFrame:
    null_count = data.isnull().sum()
    data = data.dropna()
    return data

def download_data(symbol:str):
    index = get_index_of(symbol)
    symbol_code:str
    if index == 'IDX':
        symbol_code = symbol+'.JK'
    else:
        symbol_code = symbol
    data = yfinance.download(symbol_code)
    data.to_csv(os.path.join(data_path, index, symbol+'.csv'))

def get_index_of(symbol:str):
    for index in get_index_list():
        if symbol in assets_list_from_index(index):
            return index.removesuffix('.txt')
    return None

def assets_list_from_index(index:str) -> list:
    if not '.txt' in index:
        index += '.txt'
    with open(os.path.join(index_path, index), 'r') as f:
        return f.read().splitlines()

def get_index_list():
    return os.listdir(index_path)

if __name__ == '__main__':
    download_data('TLKM')
