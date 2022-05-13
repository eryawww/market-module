import os
import pandas as pd

import core.dataprovider as dataprovider

assets = dataprovider.assets_list_from_index('IDX')
for asset in assets:
    print(asset)
    data = dataprovider.get_market_data(asset)
    data.to_csv(os.path.join('data', asset))