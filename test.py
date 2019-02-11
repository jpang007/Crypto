from pandas_datareader import data, wb
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.plotly as py

df = data.DataReader("gs", 'yahoo', datetime(2008, 1, 1), datetime(2008, 12, 28))

INCREASING_COLOR = '#17BECF'
DECREASING_COLOR = '#7F7F7F'

data = [ dict(
    type = 'candlestick',
    open = df.Open,
    high = df.High,
    low = df.Low,
    close = df.Close,
    x = df.index,
    yaxis = 'y2',
    name = 'GS',
    increasing = dict( line = dict( color = INCREASING_COLOR ) ),
    decreasing = dict( line = dict( color = DECREASING_COLOR ) ),
) ]

layout=dict()

fig = dict( data=data, layout=layout )

fig['layout'] = dict()
fig['layout']['plot_bgcolor'] = 'rgb(250, 250, 250)'
fig['layout']['xaxis'] = dict( rangeselector = dict( visible = True ) )
fig['layout']['yaxis'] = dict( domain = [0, 0.2], showticklabels = False )
fig['layout']['yaxis2'] = dict( domain = [0.2, 0.8] )
fig['layout']['legend'] = dict( orientation = 'h', y=0.9, x=0.3, yanchor='bottom' )
fig['layout']['margin'] = dict( t=40, b=40, r=40, l=40 )

colors = []

for i in range(len(df.Close)):
    if i != 0:
        if df.Close[i] > df.Close[i-1]:
            colors.append(INCREASING_COLOR)
        else:
            colors.append(DECREASING_COLOR)
    else:
        colors.append(DECREASING_COLOR)

fig['data'].append( dict( x=df.index, y=df.Volume,
                         marker=dict( color=colors ),
                         type='bar', yaxis='y', name='Volume' ) )

py.iplot( fig, filename = 'candlestick-test-3', validate = False )
