 # -*- coding: utf-8 -*-
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from layouts import CryptoGraphLayout, BotPerformanceLayout, LearningLayout, HomeLayout
import callbacks

import requests
import json
import numpy
import plotly.graph_objs as go
from datetime import datetime
import plotly.tools as tls
from flask import Flask, render_template
import dash

#index.py is responsible for controlling general flow of where the app is going

# @app.callback(Output('page-content', 'children'),
#               [Input('url', 'pathname')])
# def display_page(pathname):
#     if pathname == '/Crypto':
#         return CryptoGraphLayout
#     elif pathname == '/Bot':
#         return BotPerformanceLayout
#     elif pathname == '/Learning':
#         return LearningLayout
#     else:
#         return HomeLayout
server = Flask(__name__)
app = dash.Dash(__name__, server=server)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@server.route("/home")
def index():
    return render_template("static/index.html")

# @server.route("/graph")
# def graphLayout():
#     # @app.callback(Output('page-content', 'children'),
#     #               [Input('url', 'pathname')])
#     # def display_page(pathname):
#         return CryptoGraphLayout

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/Crypto':
        return CryptoGraphLayout
    elif pathname == '/Bot':
        return BotPerformanceLayout
    elif pathname == '/Learning':
        return LearningLayout
    else:
        return render_template("index.html")

if __name__ == '__main__':
    app.run_server(debug=True)
