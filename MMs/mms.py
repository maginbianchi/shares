from datetime import datetime, timedelta
import os
import shutil

import pandas as pd

from Common.get_data import get_data_yahoo
from Common.graficos import graficar_html, graficar

dirs = ["all conditions", "over EMA weekly", "the other ones", "xLogs"]

to_graph = {
    ("Close", "Close", "blue"),
    ("LONG_EMA", "Long EMA", "green"),
    ("SHORT_EMA", "Short EMA", "xkcd:golden")
}
to_graph2 = {
    ("LONG_EMA", "Long EMA", "green"),
    ("SHORT_EMA", "Short EMA", "gold")
}

for dir in dirs:
    if os.path.exists(dir):
        shutil.rmtree(dir)
        os.makedirs(dir)
    else:
        os.makedirs(dir)

tickers = pd.read_csv("data/shares.csv")

state = []

for index, row in tickers.iterrows():
    df = get_data_yahoo(row['TICKER'], datetime.today() - timedelta(days=730), datetime.today() + timedelta(days=1))

    print("--------------{}-------------".format(row['TICKER']))

    df['LONG_EMA'] = df.Close.ewm(span=row['LONG_EMA'], adjust=False).mean()
    df['SHORT_EMA'] = df.Close.ewm(span=row['SHORT_EMA'], adjust=False).mean()

    if (df.iloc[-1]['Close'] >= df.iloc[-1]['SHORT_EMA'] and df.iloc[-1]['SHORT_EMA'] >= df.iloc[-1]['LONG_EMA']):
        graficar_html(df, row['TICKER'], to_graph2, dirs[0])
        state.append(1)
    elif (df.iloc[-1]['Close'] >= df.iloc[-1]['LONG_EMA']):
        graficar(df, row['TICKER'], 'Date', to_graph, dirs[1])
        state.append(2)
    else:
        graficar(df, row['TICKER'], 'Date', to_graph, dirs[2])
        state.append(3)

tickers['STATE'] = state
tickers.loc[tickers.STATE == 1, 'Cathegory'] = 'All'
tickers.loc[tickers.STATE == 2, 'Cathegory'] = 'OverEMAWeekly'
tickers.loc[tickers.STATE == 3, 'Cathegory'] = 'None'

last_df = pd.read_csv("data/last_dataframe.csv")

tickers[tickers.STATE == 1].TICKER.to_csv("xLogs/AllConditions.csv", index=False)
tickers[tickers.STATE == 2].TICKER.to_csv("xLogs/OverEMAWeekly.csv", index=False)
tickers[tickers.STATE == 3].TICKER.to_csv("xLogs/TheOtherOnes.csv", index=False)

comp = tickers.merge(last_df, left_on='TICKER', right_on='TICKER')

comp[comp.STATE_x < comp.STATE_y].TICKER.to_csv("xLogs/Upgrade.csv", index=False)
comp[comp.STATE_x > comp.STATE_y].TICKER.to_csv("xLogs/Degrade.csv", index=False)

tickers.to_csv("data/last_dataframe.csv")
