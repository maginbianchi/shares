import math
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import requests
import simplejson

from Common.get_data import get_data_iol, get_data_matriz
from Common.max_min import get_max, get_min, get_max_and_min


def graficar(dfF, ticker, ind, variables, folder, lines_h, lines_v):
    fig, ax = plt.subplots(figsize=(16, 9))
    plt.title('{}'.format(ticker))
    plt.style.use('seaborn')
    for v in variables:
        ax.plot(dfF[ind], dfF[v[0]], label=v[1], color=v[2])
    for l in lines_h:
        ax.axhline(l)
    for l in lines_v:
        ax.axvline(l)
    ax.set_xlabel(ind)
    ax.set_ylabel('X')
    ax.legend()
    plt.savefig("{}/{}.png".format(folder, ticker))
    plt.close(fig)
    plt.clf()


to_graph = {
    ("Close", "Close", "blue"),
    # ("VERY_SHORT_EMA", "VERY_SHORT_EMA", "violet"),
    ("SHORT_EMA", "SHORT_EMA", "xkcd:golden"),
    # ("LONG_EMA", "LONG_EMA", "gray"),
    ("UP_LONG_EMA", "UP_LONG_EMA", "green"),
    ("DOWN_LONG_EMA", "DOWN_LONG_EMA", "red")
    # ("UP_SHORT_EMA", "UP_SHORT_EMA", "green"),
    # ("DOWN_SHORT_EMA", "DOWN_SHORT_EMA", "red")
}


def execute(df, share):
    print("--------------{}-------------".format(share))

    # Creo la EMAs y las columnas UP_LONG_EMA y DOWN_LONG_EMA para las filas cuya LONG EMA tiene cierta velocidad

    df['LONG_EMA'] = df.Close.ewm(span=120, adjust=False).mean()
    df['SHORT_EMA'] = df.Close.ewm(span=20, adjust=False).mean()
    df['VERY_SHORT_EMA'] = df.Close.ewm(span=5, adjust=False).mean()

    df.loc[(df['LONG_EMA'] - df['LONG_EMA'].shift(1)) / df['LONG_EMA'].shift(1) > 0.001, 'UP_LONG_EMA'] = df[
        'LONG_EMA']
    df.loc[(df['LONG_EMA'] - df['LONG_EMA'].shift(1)) / df['LONG_EMA'].shift(1) < -0.001, 'DOWN_LONG_EMA'] = df[
        'LONG_EMA']

    # Obtengo máximos y mínimos en el mismo DataFrame df (columnas is_max e is_min); y luego obtengo un nuevo DF
    # únicamente con los máximos y mínimos.

    get_max(df, 'High')
    get_min(df, 'Low')

    dfmym = get_max_and_min(df)

    # ------------------------------------------------------------------------------------------

    print("Reporte de entrada: ")

    # El siguiente segmento valida si se rompe un máximo o mínimo anterior (intermedio).

    if df.iloc[-1]['Close'] > df[df.is_max].iloc[-1]['High'] > df.iloc[-4]['Close']:
        print("Precio rompe máximo intermedio")

    if df.iloc[-1]['Close'] < df[df.is_min].iloc[-1]['Low'] < df.iloc[-4]['Close']:
        print("Precio rompe mínimo intermedio")

    # El siguiente segmento tiene en cuenta si la media movil LONG_EMA es positiva o negativa, y su velocidad

    if df.iloc[-1]['LONG_EMA'] >= df.iloc[-2]['LONG_EMA']:
        if not math.isnan(df.iloc[-1]['UP_LONG_EMA']):
            print("Velocidad de la EMA ascendente alta")
        else:
            print("Velocidad de la EMA ascendente normal")

    if df.iloc[-1]['LONG_EMA'] <= df.iloc[-2]['LONG_EMA']:
        if not math.isnan(df.iloc[-1]['DOWN_LONG_EMA']):
            print("Velocidad de la EMA descendente alta")
        else:
            print("Velocidad de la EMA descendente normal")

    # El siguiente segmento valida si existe una vela direccional luego de un minimo - maximo - minimo, o en su
    # defecto, luego de un maximo - minimo - maximo.

    if dfmym.iloc[-1]['is_max'] and dfmym.iloc[-2]['is_min'] and dfmym.iloc[-3]['is_max'] \
            and (dfmym.iloc[-1]['High'] > dfmym.iloc[-3]['High']) \
            and (df.iloc[-1]['Close'] >= dfmym.iloc[-2]['is_min']):
        if (df.iloc[-1]['Close'] > df.iloc[-2]['High']
                and ((df.iloc[-2]['High'] < df.iloc[-3]['High']) or (df.iloc[-3]['High'] < df.iloc[-4]['High']))):
            print("Comprar por patrón ABC y vela direccional A1")
        if df.iloc[-1]['Close'] >= df.iloc[-1]['Open'] >= (
                df.iloc[-1]['High'] - (df.iloc[-1]['High'] - df.iloc[-1]['Low']) / 3):
            print("Comprar por patrón ABC y vela rechazo alcista")

    if dfmym.iloc[-1]['is_min'] and dfmym.iloc[-2]['is_max'] and dfmym.iloc[-3]['is_min'] \
            and (dfmym.iloc[-1]['Low'] < dfmym.iloc[-3]['Low']) \
            and (df.iloc[-1]['Close'] <= dfmym.iloc[-2]['is_max']):
        if (df.iloc[-1]['Close'] < df.iloc[-2]['Low']
                and ((df.iloc[-2]['Low'] > df.iloc[-3]['Low']) or (df.iloc[-3]['Low'] > df.iloc[- 4]['High']))):
            print("Vender por patrón ABC y vela direccional B3")
        if df.iloc[-1]['Close'] <= df.iloc[-1]['Open'] <= (
                df.iloc[-1]['Low'] + (df.iloc[-1]['High'] - df.iloc[-1]['Low']) / 3):
            print("Vender por patrón ABC y vela rechazo bajista")

    # El siguiente segmento valida si existe un posible fallo en el precio de la accion.

    if (dfmym.iloc[-1]['is_max']
            and (dfmym.iloc[-1]['High'] <= dfmym.iloc[-3]['High'])
            and (dfmym.iloc[-2]['Low'] > dfmym.iloc[-4]['Low'])):
        print("Posible Fallo")
        if df.iloc[-1]['Close'] < dfmym.iloc[-2]['Low']:
            print("Fallo formado: vender")

    if (dfmym.iloc[-1]['is_min']
            and (dfmym.iloc[-1]['Low'] >= dfmym.iloc[-3]['Low'])
            and (dfmym.iloc[-2]['High'] < dfmym.iloc[-4]['High'])):
        print("Posible Fallo")
        if df.iloc[-1]['Close'] > dfmym.iloc[-2]['High']:
            print("Fallo formado: comprar")

    # El siguiente segmento valida si existe un posible Doble SoR o Trampa en el precio de la accion.

    if (dfmym.iloc[-1]['is_max']
            and (0 <= ((dfmym.iloc[-1]['High'] - dfmym.iloc[-3]['High']) / dfmym.iloc[-1]['High']) < 0.02)
            and (dfmym.iloc[-2]['Low'] > dfmym.iloc[-4]['Low'])):
        print("Posible Doble SoR o Trampa")
        if df.iloc[-1]['Close'] < dfmym.iloc[-2]['Low']:
            print("Doble SoR o Trampa formado: vender")

    if (dfmym.iloc[-1]['is_min']
            and (-0.02 < ((dfmym.iloc[-1]['Low'] - dfmym.iloc[-3]['Low']) / dfmym.iloc[-1]['Low']) <= 0)
            and (dfmym.iloc[-2]['High'] < dfmym.iloc[-4]['High'])):
        print("Posible Doble SoR o Trampa")
        if df.iloc[-1]['Close'] > dfmym.iloc[-2]['High']:
            print("Doble SoR o Trampa formado: comprar")

    # El siguiente segmento valida si una vela cambia de sentido en un retroceso.

    if ((df.iloc[-1]['Close'] > df.iloc[-2]['High'])
            and ((df.iloc[-2]['High'] < df.iloc[-3]['High']) or (df.iloc[-3]['High'] < df.iloc[-4]['High']))):
        print("Vela direccional alcista")

    if ((df.iloc[-1]['Close'] < df.iloc[-2]['Low'])
            and ((df.iloc[-2]['Low'] > df.iloc[-3]['Low']) or (df.iloc[-3]['Low'] > df.iloc[-4]['High']))):
        print("Vela direccional bajista")

    # ------------------------------------------------------------------------------------------

    print("\nReporte de salida: ")

    # El siguiente segmento valida si el precio quiebra la EMA más corta, dando una posible salida
    print("Si estas dentro del mercado bajista: ")

    if df.iloc[-1]['Close'] <= df.iloc[-1]['VERY_SHORT_EMA']:
        print("Continuar en mercado.")
    else:
        print("Salir del mercado.")

    print("Si estas dentro del mercado alcista: ")

    if df.iloc[-1]['Close'] >= df.iloc[-1]['VERY_SHORT_EMA']:
        print("Continuar en mercado.")
    else:
        print("Salir del mercado.")

    # ------------------------------------------------------------------------------------------

    graficar(df,
             share,
             'Date',
             to_graph,
             "graficos",
             pd.concat([df[df.is_max]['High'].tail(1),
                        df[df.is_min]['Low'].tail(1)]),
             [])
    # print(dfmym[dfmym.fail]['Date'])
    # print(dfmym[dfmym.double_rs]['Date'])
    # print(dfmym[dfmym.reversion]['Date'])

    print("--------Finalizado {}--------".format(share))


if __name__ == "__main__":
    shares = [["GGAL", "NYSE"],
              ["TX", "NYSE"],
              ["MIRG", "BCBA"],
              ["ALUA", "BCBA"],
              ["AGRO", "BCBA"],
              ["BYMA", "BCBA"],
              ["CVH", "BCBA"],
              ["TGNO4", "BCBA"],
              ["TRAN", "BCBA"],
              ["DGCU2", "BCBA"],
              ["METR", "BCBA"],
              ["YPF", "NYSE"],
              ["PAM", "NYSE"],
              ["BBAR", "NYSE"],
              ["BMA", "NYSE"],
              ["TEO", "NYSE"],
              ["TGS", "NYSE"],
              ["EDN", "NYSE"],
              ["CRESY", "NYSE"],
              ["COME", "BCBA"],
              ["LOMA", "NYSE"],
              ["AC17D", "BCBA"],
              ["AY24D", "BCBA"],
              ["HARG", "BCBA"],
              ["CEPU", "NYSE"]]
    # shares = [["GGAL", "NYSE"]]

    for share in shares:
        df = get_data_iol(share[0], share[1], str(int(((datetime.now() - timedelta(days=364)).timestamp()))),
                          str(int((datetime.now().timestamp()))), "D")
        execute(df, share[0])
    df = get_data_matriz("I_RFX20", "2019-01-01", "2020-01-20", "D")
    execute(df, "Rofex20")
    df = get_data_matriz("I_RFX20", "2020-01-13", "2020-01-20", "1")
    execute(df, "Rofex20_1m")
