import os
import pandas as pd

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
        return pd.read_csv(data_source, index_col=0)

if __name__ == '__main__':
    df = get_market_data('TLKM')
