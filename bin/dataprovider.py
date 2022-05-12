import os
import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    filename= 'runtime.log',
)

data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

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
    if null_count.sum() > 0:
        logging.warning(f"{null_count} rows are null")
        logging.warning(data[data.isnull().any(axis=1)])
    data = data.dropna()
    return data

if __name__ == '__main__':
    df = get_market_data('TLKM')
