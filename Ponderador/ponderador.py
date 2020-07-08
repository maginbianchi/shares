import sched
import time
from datetime import datetime, timedelta

import pandas as pd

from Common.get_data import get_data_yahoo
from Common.graficos import graficar

dfc = pd.DataFrame(columns=['Time', 'Ponderacion', 'PonderacionUSD'])
i = 0

to_graph = {
    ("Ponderacion", "Ponderacion", "blue"),
    ("EMA20", "EMA 20", "xkcd:golden"),
    ("EMA120", "EMA 120", "violet")
}

to_graph_USD = {
    ("Ponderacion", "Ponderacion", "blue"),
    ("PonderacionUSD", "Ponderacion U$D", "green")
}


def calcular(sc):
    global dfc
    global i
    try:
        adrs = [("BBAR", 0.0309),
                ("BMA", 0.0971),
                ("SUPV", 0.0186),
                ("CEPU", 0.0655),
                ("CRESY", 0.0163),
                ("EDN", 0.0186),
                ("GGAL", 0.1440),
                ("PAM", 0.0765),
                ("PBR", 0.1855),
                ("TS", 0.0669),
                ("TX", 0.0301),
                ("TGS", 0.0469),
                ("YPF", 0.1081)]

        total = 0
        for adr in adrs:
            total += adr[1]

        ponderador = total
        ponderacion = 0
        ponderacionUSD = 0

        dfd = get_data_yahoo("USDARS=X", datetime.today() - timedelta(days=4), datetime.today() + timedelta(days=1))
        variacionUSD = (dfd.iloc[-1]['Close'] - dfd.iloc[-1]['Open']) / dfd.iloc[-1]['Open']

        for adr in adrs:
            df = get_data_yahoo(adr[0], datetime.today() - timedelta(days=4), datetime.today() + timedelta(days=1))

            variacion = (df.iloc[-1]['Close'] - df.iloc[-2]['Close']) * 100 / df.iloc[-2]['Close']
            variacionD = (df.iloc[-1]['Close'] * (1 + variacionUSD) - df.iloc[-2]['Close']) * 100 / df.iloc[-2]['Close']
            ponderacion += variacion * adr[1] / ponderador
            ponderacionUSD += variacionD * adr[1] / ponderador
            print("{} {}%".format(adr[0], round(variacion, 2)))

        print("\n{} {}%".format("Dolar", round(variacionUSD * 100, 2)))

        print("\nPonderación: {}%".format(ponderacion))
        print("Ponderación USD: {}%\n\n".format(ponderacionUSD))

        dfc.loc[i] = [datetime.now().time(), ponderacion, ponderacionUSD]
        i += 1

        df_aux= dfc.copy()
        df_aux['EMA20'] = dfc['Ponderacion'].ewm(span=20, adjust=False).mean()
        df_aux['EMA120'] = dfc['Ponderacion'].ewm(span=120, adjust=False).mean()

        graficar(df_aux, "Ponderador1", 'Time', to_graph, '.')
        graficar(dfc, "Ponderador2", 'Time', to_graph_USD, '.')
    except Exception as e:
        print(e)
    s.enter(15, 1, calcular, (sc,))


s = sched.scheduler(time.time, time.sleep)

s.enter(0, 1, calcular, (s,))
s.run()
