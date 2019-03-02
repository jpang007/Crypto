 # -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from layouts import cryptoGraphLayout, page_2_layout, index_page
import callbacks

import requests
import json
import numpy
import plotly.graph_objs as go
from datetime import datetime
import plotly.tools as tls

#index.py is responsible for controlling general flow of where the app is going

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page-1':
        return cryptoGraphLayout
    elif pathname == '/page-2':
        return page_2_layout
    else:
        return index_page

if __name__ == '__main__':
    app.run_server(debug=True)
