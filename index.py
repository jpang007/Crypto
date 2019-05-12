 # -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app, server
from layouts import CryptoGraphLayout, BackTestLayout
import callbacks

import requests
import json
import numpy
import plotly.graph_objs as go
from datetime import datetime
import plotly.tools as tls
from flask import Flask, render_template

#index.py is responsible for controlling general flow of where the app is going

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content', style={'backgroundColor': '#D3D3D3'})
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return CryptoGraphLayout
    elif pathname == '/backtest':
         return BackTestLayout
    else:
        return '404'


if __name__ == '__main__':
    app.run_server(debug=True)
