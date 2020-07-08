import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from math import pi

from bokeh.plotting import figure, save, output_file

def graficar(dfF, ticker, ind, variables,  folder):
    fig, ax = plt.subplots(figsize=(16,9))
    plt.title('{}'.format(ticker))
    plt.style.use('seaborn')
    for v in variables:
        ax.plot(dfF[ind], dfF[v[0]], label=v[1], color=v[2])

    ax.set_xlabel(ind)
    ax.set_ylabel('X')
    ax.legend()
    plt.savefig("{}/{}.png".format(folder, ticker))  
    plt.close(fig)
    plt.clf()

def graficar_html(df, ticker, variables, folder):
    inc = df.Close > df.Open
    dec = df.Open > df.Close
    w = 12*60*60*1000 # half day in ms

    TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

    p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=1000, title = ticker)
    p.xaxis.major_label_orientation = pi/4
    p.grid.grid_line_alpha=0.3

    p.segment(df.Date, df.High, df.Date, df.Low, color="black")
    p.vbar(df.Date[inc], w, df.Open[inc], df.Close[inc], fill_color="green", line_color="black")
    p.vbar(df.Date[dec], w, df.Open[dec], df.Close[dec], fill_color="red", line_color="black")
    for v in variables:
        p.line(df.Date, df[v[0]], name=v[1], color=v[2])

    output_file("{}/{}.html".format(folder, ticker), title=ticker)
    save(p)