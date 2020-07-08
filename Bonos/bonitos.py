from datetime import datetime, timedelta

from Common.get_data import get_data_iol
from Common.graficos import graficar

bonos = ["AO20D", "AY24D", "DICAD", "AA37D", "AC17D"]

to_graph = {
    ("Close", "Close", "blue"),
    ("LONG_EMA", "Long EMA", "green"),
    ("SHORT_EMA", "Short EMA", "xkcd:golden")
}

for bono in bonos:
    df = get_data_iol(bono, "BCBA", str(int(((datetime.now() - timedelta(days=364)).timestamp()))),
                      str(int((datetime.now().timestamp()))), "D")

    print("--------------{}-------------".format(bono))

    df['LONG_EMA'] = df.Close.ewm(span=150, adjust=False).mean()
    df['SHORT_EMA'] = df.Close.ewm(span=20, adjust=False).mean()

    graficar(df, bono, 'Date', to_graph, "graficos")

# df1 = get_data_iol("AC17D", "BCBA", "1514216806", "1575320866", "D")
# df2 = get_data_iol("AA37D", "BCBA", "1514216806", "1575320866", "D")
#
# df = df1.merge(df2, left_on='Date', right_on='Date')
# df['Cociente'] = df['Close_x'] / df['Close_y']
#
# graficar(df, "sarasa")
