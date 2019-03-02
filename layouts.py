import dash_core_components as dcc
import dash_html_components as html
#handles setup of the layouts 
index_page = html.Div([
    dcc.Link('Go to Page 1', href='/page-1'),
    html.Br(),
    dcc.Link('Go to Page 2', href='/page-2'),
])

cryptoGraphLayout = html.Div(children=[
    html.H1(
        id = 'title',
        children='Bitcoin Graph',
        style={
            'textAlign': 'center',
        }
    ),

    # represents the URL bar, doesn't render anything
    dcc.Link('Navigate to "/"', href='/'),
    html.Br(),
    dcc.Link('Navigate to "/page-2"', href='/page-2'),

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

page_2_layout = html.Div([
    html.H1('Page 2'),
    dcc.RadioItems(
        id='page-2-radios',
        options=[{'label': i, 'value': i} for i in ['Orange', 'Blue', 'Red']],
        value='Orange'
    ),
    html.Div(id='page-2-content'),
    html.Br(),
    dcc.Link('Go to Page 1', href='/page-1'),
    html.Br(),
    dcc.Link('Go back to home', href='/')
])
