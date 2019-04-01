import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
import datetime

colors = {
    'background': '#D3D3D3',
    'text': '#7FDBFF'
}
CryptoGraphLayout = html.Div(children=[
        html.Div([
            dcc.Dropdown(
                id='crypto-type',
                options=[
                    {'label': 'Bitcoin', 'value': 'BTC'},
                    {'label': 'Ethereum', 'value': 'ETH'},
                    {'label': 'Litecoin', 'value': 'LTC'}
                ],
                value='BTC'
                ),
        ],
        style = {'margin-bottom':'30px'}),

        html.Div([
            dcc.DatePickerRange(
                id='my-date-picker-range',
                min_date_allowed=dt(1995, 8, 5),
                max_date_allowed=datetime.datetime.now() - datetime.timedelta(days=1),
                initial_visible_month=datetime.datetime.now(),
                updatemode='bothdates'
            )
        ],
        style={'float':'right', 'margin-right': '100px'}),

        html.Div([
                html.Button('Last 30 Days', id='btn-1'),
                html.Button('Last 90 Days', id='btn-2'),
                html.Button('Last 180 Days', id='btn-3'),
                html.Button('Reset Graph', id='btn-4')
        ],
        style={'margin-bottom':'30px', 'color':'white', 'margin-left': '100px'}),

        dcc.Graph(
            id='bitcoin-graph'
        ),

        dcc.Graph(
            id = 'rsi-graph'
        )
],      style={'backgroundColor':'#D3D3D3'})
