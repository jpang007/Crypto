import dash_core_components as dcc
import dash_html_components as html
#handles setup of the layouts
HomeLayout = html.Div([
    dcc.Link('Go to Crypto Chart', href='/Crypto'),
    html.Br(),
    dcc.Link('Go to Bot Performance', href='/Bot'),
    html.Br(),
    dcc.Link('Go to Learning', href='/Learning'),
])

CryptoGraphLayout = html.Div(children=[
    # html.H1(
    #     id = 'title',
    #     children='Bitcoin Graph',
    #     style={
    #         'textAlign': 'center',
    #     }
    # ),

    # link block
    # dcc.Link('Go to Home', href='/'),
    # html.Br(),
    # dcc.Link('Go to Bot Performance', href='/Bot'),
    # html.Br(),
    # dcc.Link('Go to Learning', href='/Learning'),

    # content will be rendered in this element

    html.Div(
        children='Charting cryptocurrency with technical analysis (and with style!)',
        style={'textAlign': 'center',
    }),

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
    ]),

    dcc.Graph(
        id='bitcoin-graph'
    ),

    dcc.Graph(
        id = 'rsi-graph'
    )
])

BotPerformanceLayout = html.Div([
    html.H1('Page 2'),
    dcc.RadioItems(
        id='page-2-radios',
        options=[{'label': i, 'value': i} for i in ['Orange', 'Blue', 'Red']],
        value='Orange'
    ),
    dcc.Link('Go to Home', href='/'),
    html.Br(),
    dcc.Link('Go to Crypto Chart', href='/Crypto'),
    html.Br(),
    dcc.Link('Go to Learning', href='/Learning'),
])

LearningLayout = html.Div([
    html.H1('Page 2'),
    dcc.RadioItems(
        id='page-2-radios',
        options=[{'label': i, 'value': i} for i in ['Orange', 'Blue', 'Red']],
        value='Orange'
    ),
    dcc.Link('Go to Home', href='/'),
    html.Br(),
    dcc.Link('Go to Crypto Chart', href='/Crypto'),
    html.Br(),
    dcc.Link('Go to Bot Performance', href='/Bot'),
])
