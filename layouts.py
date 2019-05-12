import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dt
import dash_table
import datetime

colors = {
    'background': '#D3D3D3',
    'text': '#7FDBFF'
}
CryptoGraphLayout = html.Div(children=[
        dcc.Link('Go to Backtesting', href='/backtest'),
        html.Div([
                html.P('Choose a cryptocurrency'),
        ], style={'font-size':'30px', 'text-align':'center'}),
        html.Div([
            html.Img(src='../assets/bitcoin.svg', width="150px", height="150px", style={'padding-right': '20px', 'cursor': 'pointer'}, id="bitcoinImg"),
            html.Img(src='../assets/litecoin.svg', width="150px", height="150px", style={'cursor': 'pointer'}, id="litecoinImg"),
            html.Img(src='../assets/ethereum.svg', width="150px", height="150px", style={'cursor': 'pointer'}, id="ethereumImg"),
        ],
        style={'margin-bottom':'30px', 'display': 'flex', 'justify-content': 'center', 'margin-left': 'auto', 'margin-right': 'auto'}),

        html.Div([
            html.P('Choose indicators:'),
            ], style={'font-size':'30px', 'text-align':'center'}),

        html.Div([
            dcc.Checklist(
                id = 'techIndicators',
                options=[
                    {'label': 'RSI', 'value': 'RSI'},
                    {'label': 'Bollinger Bands', 'value': 'BB'},
                    {'label': 'MACD', 'value': 'MAC'}
                ],
                values=['RSI', 'BB', 'MAC'], labelStyle={'display': 'inline-block', 'margin': '0 10px 0 10px'}, style={'zoom':'1.5'}
                )
        ],
        style = {'margin-bottom':'30px', 'display': 'flex', 'justify-content': 'center', 'margin-left': 'auto', 'margin-right': 'auto'}),

        html.Div([
            dcc.DatePickerRange(
                id='my-date-picker-range',
                min_date_allowed=dt(1995, 8, 5),
                max_date_allowed=datetime.datetime.now() - datetime.timedelta(days=1),
                initial_visible_month=datetime.datetime.now(),
                updatemode='bothdates'
            )
        ],
        style={'float':'right', 'margin-right': '10%'}),

        html.Div([
                html.Button('Last 30 Days', id='btn-1'),
                html.Button('Last 90 Days', id='btn-2'),
                html.Button('Last 180 Days', id='btn-3'),
                html.Button('Reset Graph', id='btn-4')
        ],
        style={'margin-bottom':'30px', 'color':'white', 'margin-left': '10%'}),

        html.Div([
                html.P('To Date Gain Percentage'),
                html.P(id = "graphRangePercentage",
                   children=[""])
        ], style={'font-size':'30px', 'text-align':'center'}),

        dcc.Graph(
            id='bitcoin-graph',
            figure={
                'layout': {
                    'plot_bgcolor': '#D3D3D3',
                    'paper_bgcolor': '#D3D3D3'
                }
            }
        ),

        html.Div(id="macd-container", children= [
            dcc.Graph(
                id='macd-graph',
                figure={
                    'layout': {
                        'plot_bgcolor': '#D3D3D3',
                        'paper_bgcolor': '#D3D3D3'
                    }
                }
            ),
        ]),

        html.Div(id="rsi-container", children= [
          dcc.Graph(
              id = 'rsi-graph',
              figure={
                  'layout': {
                      'plot_bgcolor': '#D3D3D3',
                      'paper_bgcolor': '#D3D3D3'
                  }
              }
          ),
        ])

],      style={'backgroundColor':'#D3D3D3'})

params = [
    'Trade Date', 'Decision', 'Price Filled', 'Total Return', 'Total Return Percent'
]

BackTestLayout = html.Div(children=[

            html.Div([
                    html.P('Choose a cryptocurrency'),
            ], style={'font-size':'30px', 'text-align':'center'}),

            html.Div([
                html.Img(src='../assets/bitcoin.svg', width="150px", height="150px", style={'padding-right': '20px', 'cursor': 'pointer'}, id="bitcoinBacktestImg"),
                html.Img(src='../assets/litecoin.svg', width="150px", height="150px", style={'cursor': 'pointer'}, id="litecoinBacktestImg"),
                html.Img(src='../assets/ethereum.svg', width="150px", height="150px", style={'cursor': 'pointer'}, id="ethereumBacktestImg"),
            ], style={'display': 'flex', 'justify-content': 'center', 'margin-left': 'auto', 'margin-right': 'auto', 'class': 'myClass', 'margin-bottom': '30px'}),

            html.Div([
                    html.P('Currently using: '),
                    html.P(id = "currentCoin",
                       children=[""])
            ], style={'font-size':'30px', 'text-align':'center'}),

            html.Div([
                    html.P('Choose a trading method'),
            ], style={'font-size':'30px', 'text-align':'center', 'text-decoration': 'underline'}),

            html.Div(id="radio-container-2", children= [
                html.P('Advanced strategies:'),
                dcc.RadioItems(
                id="radioItems2",
                options=[
                    {'label': 'RSI + Stochastic', 'value': 'RSIS'},
                    {'label': 'Bollinger Counter-Trend System', 'value': 'BBC'},
                    {'label': 'EMA Crossover', 'value': 'EMA'}
                ]
                ),
            ], style = {'float':'right', 'zoom':'1.5', 'margin-right': '30%'}),

            html.Div(id="radio-container-1", children= [
                html.P('Basic strategies:'),
                dcc.RadioItems(
                id="radioItems1",
                options=[
                    {'label': 'RSI', 'value': 'RSI'},
                    {'label': 'Bollinger Bands', 'value': 'BB'},
                    {'label': 'MACD', 'value': 'MAC'},
                ]
                ),
            ], style = {'margin-bottom': '30px', 'zoom':'1.5', 'margin-left': '35%'}),

            html.Div([
                html.P('Customizable Configurations'),
                html.P('Test Dollars:'),
                dcc.Input(id='input-1-submit', type='number', value=1000)
            ], style={'font-size':'30px', 'text-align':'center', 'margin-bottom':'30px'}),

            html.Div([
            html.P('Backtesting Trading Overall Percent Change'),
            html.P(
            id = "backtestPercent",
            children=[""]),
            ], style={'font-size':'30px', 'text-align':'center'}),

            html.Div([
                'Trade History',
                html.Span('Using your selected trading method, the chart generated will display the list of trades performed.', className = 'top')
            ], className = 'tooltip', style={'font-size':'30px', 'margin-bottom':'30px'}),

            html.Div([
            dash_table.DataTable(
                id='tradeTable',
                columns=(
                    [{'id': 'Trade Number', 'name': 'Trade Number'}] +
                    [{'id': p, 'name': p} for p in params]
                ),
                style_cell_conditional=[
                      {'if': {'column_id': 'Trade Number'},
                       'width': '16%', 'textAlign': 'left'},
                      {'if': {'column_id': 'Trade Date'},
                       'width': '16%', 'textAlign': 'left'},
                      {'if': {'column_id': 'Decision'},
                       'width': '16%', 'textAlign': 'left'},
                      {'if': {'column_id': 'Price Filled'},
                       'width': '16%', 'textAlign': 'left'},
                      {'if': {'column_id': 'Total Return'},
                       'width': '16%', 'textAlign': 'left'},
                      {'if': {'column_id': 'Total Return Percent'},
                       'width': '16%', 'textAlign': 'left'},
                ]
            )
            ], style={'font-size':'30px'}),

            dcc.Link('Go to graph', href='/')
], style={'backgroundColor':'#D3D3D3'})
