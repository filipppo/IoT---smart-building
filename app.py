import math
import numpy as np
import pandas as pd
import datetime
import time
import urllib.request


from bokeh.embed import components
from bokeh.models import Slider,Legend
from bokeh.plotting import figure
from bokeh.transform import factor_cmap
from bokeh.layouts import column, row

from flask import Flask, render_template, request

from connect import *

app = Flask(__name__)

wiatrak=0

@app.route('/',methods=['GET', 'POST'])
def chart():
    if request.method == "POST":
        global wiatrak

        field = request.form['slider_field']
        field=int(field)
        start = request.form['slider_start']
        end = request.form['slider_end']
        start=convert_string_to_date2(start)
        end=convert_string_to_date2(end)
        start_time = time.time()
        data = prepare_data(field,start,end)
        print("--- %s seconds ---" % (time.time() - start_time))
        x_axis, y_axis = create_x_y_axis(data)
        script_data_plot, div_data_plot = components(draw_plot(field,start,end,x_axis,y_axis))
        return render_template('index.html',
            div_data_plot=div_data_plot,script_data_plot=script_data_plot,
            field=field,
            start=start,
            end=end,
            wiatrak=wiatrak,
            srednia=get_avg_val(y_axis),
            min=get_min_val(y_axis),
            max=get_max_val(y_axis),
            amp=get_amplitude_val(y_axis),
        )
    return render_template('index.html',wiatrak=wiatrak)

@app.route('/send',methods=['GET', 'POST'])
def send():
        global wiatrak

        if(wiatrak==0):wiatrak=1
        else: wiatrak=0
        urllib.request.urlopen(f"https://api.thingspeak.com/update?api_key=J48OGT1O14S0S1QB&field1={wiatrak}")
        print(str(wiatrak))

        return render_template('index.html',
        wiatrak=wiatrak
        )

def create_x_y_axis(data_list):
    x_axis = []
    y_axis = []
    for record in data_list:
        x_axis.append(record['created_at'])
        y_axis.append(record['value'])
    return x_axis, y_axis

def plot_line_styler(p):
    p.title.text_font_size = "25px"
    p.title.text_font_style = "bold"
    p.title.align = "center"
    #p.title.background_fill_color = "#033a63"
    p.title.text_color = "#033a63"
    p.axis.axis_label_text_font_style = "bold"
    p.axis.axis_label_text_font_size = "15pt"
    p.axis.axis_label_text_color = "#033a63"

def draw_plot(field,start,end,x_axis,y_axis):
    y_label=""
    title=""
    def switch(field):
        if field == 1:
            y_label="[°C]"
            title="Temperatura [°C]"
        elif field == 2:
            y_label=""
            title="Ruch"
        elif field == 3:
            y_label=""
            title="Stan wiatraka"
        elif field == 4:
            y_label="[hPa]"
            title="Ciśnienie atm. (BMP-180) [hPa]"
        elif field == 5:
            y_label="[°C]"
            title="Temp. grzejnika (DS18B20) [°C]"
        elif field == 6:
            y_label="[°C]"
            title="Temperatura (DS18B20) [°C]"
        elif field == 7:
            y_label=""
            title="Ruch (PIR)"
        elif field == 8:
            y_label="[°C]"
            title="Temperatura (BMP-180) [°C]"
        return y_label,title
    y_label,title = switch(field)
    p = figure(x_range=(start, end),title=title,x_axis_type='datetime', x_axis_label="Data", y_axis_label=y_label, width=880, height=660)
    w1=p.line(x_axis, y_axis,line_width=2, color="#033a63")
    plot_line_styler(p)

    return p

if __name__ == '__main__':
    app.run(debug=True)