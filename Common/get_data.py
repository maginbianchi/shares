import yfinance as yf
import pandas as pd
import pandas_datareader.data as web
import requests
import simplejson

yf.pdr_override()
urliol_historico = "https://www.invertironline.com/api/cotizaciones/history?symbolName={}&exchange={}&from={}&to={}&resolution={}";
matriz_historico = "https://rofex.primary.ventures/api/v2/series/securities/rx_DUAL_{}?resolution={}&from" \
                   "={}T23%3A44%3A20.000Z&to={}T23%3A44%3A20.000Z"


def get_data_yahoo(ticker, start, end):
    # Creo el dataframe con los datos financieros
    df = web.get_data_yahoo(ticker, start, end)

    # Seteo el indice de fecha como una columna
    df = df.reset_index(level=0)

    return df


def get_data_iol(ticker, mercado, from_date, to_date, time_frame):
    r = requests.get(urliol_historico.format(ticker, mercado, from_date, to_date, time_frame))
    data = simplejson.loads(r.text)
    df = pd.DataFrame.from_dict(data['bars'])
    df['Date'] = pd.to_datetime(df['time'], unit='s').dt.date
    df = df.rename(columns={'time': 'Time', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close',
                            'volume': 'Volume'})
    df = df.reset_index(level=0)
    df.set_index('Date')
    # del df['index']
    return df


def get_data_matriz(ticker, from_date, to_date, time_frame):
    r = requests.get(matriz_historico.format(ticker, time_frame, from_date, to_date))
    data = simplejson.loads(r.text)
    df = pd.DataFrame.from_dict(data['series'])
    df = df.rename(columns={'d': 'Date', 'c': 'Close', 'o': 'Open', 'h': 'High', 'l': 'Low',
                            'v': 'Volume'})
    df = df.reset_index(level=0)
    df.set_index('Date')
    # del df['index']
    return df
