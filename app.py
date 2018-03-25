from flask import Flask, render_template, request, redirect
import requests
import simplejson as json
import pandas as pd
import numpy as np
import datetime
import dateutil.relativedelta
from bokeh.plotting import figure, output_file, show

import os
from bokeh.embed import components
from bokeh.models import DatetimeTickFormatter
from bokeh.palettes import Spectral4
from math import pi

def FindData(ticker,features):
  end = datetime.datetime.now()
  end_date = end.strftime("%Y-%m-%d")
  start = end + dateutil.relativedelta.relativedelta(months=-1)
  start_date = start.strftime("%Y-%m-%d")

  cols = ",".join(features)
  url = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?&ticker=' + ticker + '&qopts.columns=date,' + cols +'&api_key=' + SaraKEY

  r = requests.get(url).json()   
  r = pd.DataFrame(r[u'datatable'][u'data']) 
  last_month_r = r[r[0] >= start_date]
  last_month_r.columns = ['date'] + features
  temp = pd.to_datetime(last_month_r['date'])
  last_month_r.loc[:,'date'] = temp
  return last_month_r

def plot(r,features):
  
  p = figure(x_axis_type='datetime', plot_width=600, plot_height=600, title="Quandl WIKI EOD Stock Prices-last month")

  for i,name,color in zip(range(len(features)),features,Spectral4):
    p.line(r['date'], r[features[i]],color=color, legend=name)
  p.xaxis.formatter=DatetimeTickFormatter(
        hours=["%d %B %Y"],
        days=["%d %B %Y"],
        months=["%d %B %Y"],
        years=["%d %B %Y"],
    )
  p.xaxis.major_label_orientation = pi/4
  return p



app = Flask(__name__)

@app.route('/')
def index():
  return render_template('info.html')

@app.route('/graph',methods=['GET', 'POST'])
def responses():
  if request.method == 'GET':
    return redirect('/')
  else:
    features = request.form.getlist('features')
    ticker  = request.form['ticker']
    
    if ticker == "" or features == [] :
      return redirect('/')
    else:
      r = FindData(ticker,features)
      p = plot(r,features)
      script, div = components(p)
      return render_template('graph.html',script = script, div = div)
    


if __name__ == '__main__':
  SaraKEY = os.environ.get('myQuandlKEY')
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port)
#  app.run(port=33507)
