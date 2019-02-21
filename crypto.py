 # -*- coding: utf-8 -*-
import requests
import json
import numpy
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from datetime import datetime
from dash.dependencies import Input, Output
import plotly.tools as tls

#calculates average gain and loss over a period (usually 14)
def calcDailyGains(ClosingPrice, RSIPeriod):
    AverageGain = []
    AverageLoss = []
    CurrentChange = 0
    for i, j in enumerate(range(0,RSIPeriod - 1)):
        Change = ClosingPrice[i + 1] - ClosingPrice[i]
        if Change > 0:
            AverageGain.append(Change)
        else:
            AverageLoss.append(Change)
        #current gain
        if j == RSIPeriod - 2:
            if Change > 0:
                CurrentChange = Change
            else:
                CurrentChange = Change

    TotalAverageGain = (sum(AverageGain) / RSIPeriod)
    TotalAverageLoss = (sum(AverageLoss) / RSIPeriod)

    return TotalAverageGain, TotalAverageLoss, CurrentChange

#calculates simple moving average over a period (usually 20)
#returns values for middle upper and lower band
def calcSMA(ClosingPrice, BandPeriod):
    MiddleBand = (sum(ClosingPrice) / BandPeriod)
    StandardDeviation = numpy.std(ClosingPrice)
    UpperBand = MiddleBand + (StandardDeviation * 2)
    LowerBand = MiddleBand - (StandardDeviation * 2)
    return LowerBand, MiddleBand, UpperBand

#Formula to calculate RSI using average gain and loss
def calcRSI(TotalAverageGain, TotalAverageLoss, CurrentChange, RSIPeriod):
    CurrentGain = 0
    CurrentLoss = 0
    firstRSI = TotalAverageGain / abs(TotalAverageLoss)
    RSI = 100 - (100 / (1 + firstRSI))
    #print (RSI) not smoothed

    if CurrentChange > 0:
        CurrentGain = CurrentChange
    else:
        CurrentLoss = CurrentChange

    #smoothRSI
    smoothRSI = (((TotalAverageGain * (RSIPeriod - 1)) + CurrentGain) / RSIPeriod) / (((abs(TotalAverageLoss) * (RSIPeriod - 1)) + CurrentLoss) / RSIPeriod)
    finalRSI = 100 - (100 / (1 + smoothRSI))
    return finalRSI

def getAPI(DaysToStore):
    #Get's the current price
    currentprice = requests.get("https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,LTC&tsyms=USD&api_key=0bfac81ab05f7e572f8cc18a28a05c6c2f3665a10d17099efe1d7c2e3b3e0195")
    pricedata = currentprice.json()
    print (pricedata)

    bitcoinHistorical = requests.get("https://min-api.cryptocompare.com/data/histoday?fsym=BTC&tsym=USD&limit=" + str(DaysToStore) + "&api_key=0bfac81ab05f7e572f8cc18a28a05c6c2f3665a10d17099efe1d7c2e3b3e0195")
    bitcoinHistoricalData = bitcoinHistorical.json()
    print (bitcoinHistoricalData['Data'])
    return bitcoinHistoricalData

#init block
DaysToDisplay = 30
DaysToStore = DaysToDisplay + 20 #Must always be 20 days greater than DaysToDisplay
CurrentDay = 30
bitcoinHistoricalData = getAPI(DaysToStore)
RSIClosingPrice, BandClosingPrice, RSIValues, LowerBandValues, MiddleBandValues, UpperBandValues = ([] for i in range(6))
RSIPeriod = 14
BandPeriod = 20

#block for RSI calcuation
for i in range(0, DaysToDisplay):
    RSIClosingPrice = [] #reset the list
    for i in range(CurrentDay - RSIPeriod, CurrentDay):
        #RSIClosingPrice.append(bitcoinHistoricalData[i]['close'])
        RSIClosingPrice.append(bitcoinHistoricalData['Data'][i]['close'])
    TotalAverageGain, TotalAverageLoss, CurrentChange = calcDailyGains(RSIClosingPrice, RSIPeriod)
    finalRSI = calcRSI(TotalAverageGain, TotalAverageLoss, CurrentChange, RSIPeriod)
    RSIValues.append(finalRSI)
    CurrentDay = CurrentDay - 1

print (RSIValues)
#block for bollinger band calculation
for i in range(0, DaysToDisplay):
    BandClosingPrice = [] #reset the list
    for i in range(CurrentDay - BandPeriod, CurrentDay):
        #BandClosingPrice.append(bitcoinHistoricalData[i]['close'])
        BandClosingPrice.append(bitcoinHistoricalData['Data'][i]['close'])
    LowerBand, MiddleBand, UpperBand = calcSMA(BandClosingPrice, BandPeriod)
    LowerBandValues.append(LowerBand)
    MiddleBandValues.append(MiddleBand)
    UpperBandValues.append(UpperBand)
    CurrentDay = CurrentDay - 1

print (LowerBandValues, MiddleBandValues, UpperBandValues)

#Dash Graphing
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
INCREASING_COLOR = '#17BECF'
DECREASING_COLOR = '#7F7F7F'
graphOpen, graphClose, graphHigh, graphLow, graphDate, graphVolume, graphRSI, graphBand = ([] for i in range(8))
for i in range(DaysToStore - DaysToDisplay, DaysToStore):
    graphOpen.append(bitcoinHistoricalData['Data'][i]['open'])
    graphClose.append(bitcoinHistoricalData['Data'][i]['close'])
    graphHigh.append(bitcoinHistoricalData['Data'][i]['high'])
    graphLow.append(bitcoinHistoricalData['Data'][i]['close'])
    graphDate.append(datetime.utcfromtimestamp(bitcoinHistoricalData['Data'][i]['time']).strftime('%Y-%m-%d %H:%M:%S'))
    graphVolume.append(bitcoinHistoricalData['Data'][i]['volumeto'])
    # graphOpen.append(bitcoinHistoricalData[i]['open'])
    # graphClose.append(bitcoinHistoricalData[i]['close'])
    # graphHigh.append(bitcoinHistoricalData[i]['high'])
    # graphLow.append(bitcoinHistoricalData[i]['close'])
    # graphDate.append(datetime.utcfromtimestamp(bitcoinHistoricalData[i]['time']).strftime('%Y-%m-%d %H:%M:%S'))
    # graphVolume.append(bitcoinHistoricalData[i]['volumeto'])

app.layout = html.Div(children=[
    html.H1(
        id = 'title',
        children='Bitcoin Graph',
        style={
            'textAlign': 'center',
        }
    ),

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
    )


])
#
# @app.callback(
#     Output(component_id='my-div', component_property='children'),
#     [Input(component_id='my-id', component_property='value')]
# )
# def update_output_div(input_value):
#     return 'You\'ve entered "{}"'.format(input_value)

#Callback for dynamic graph
@app.callback(
        Output('bitcoin-graph', 'figure'),
        [Input(component_id='crypto-type', component_property = 'value')]
        )
def update_graph(crypto_value):
    traces = []
    traces.append(go.Candlestick(
        x = graphDate,
        open = graphOpen,
        high = graphHigh,
        low = graphLow,
        close = graphClose,
        yaxis='y2',
        name = 'Closing Price',
        increasing = dict( line = dict( color = INCREASING_COLOR ) ),
        decreasing = dict( line = dict( color = DECREASING_COLOR ) ),
        ))
    traces.append(go.Bar(
        x=graphDate,
        y=graphVolume,
        yaxis='y',
        name = 'Volume',
        marker = dict(color=INCREASING_COLOR)
    ))

    return {
        'data': traces,
        'layout': go.Layout(
            title = (crypto_value) + ' Graph',
            xaxis = dict(
                rangeslider = dict( visible = False ),
            ),
            yaxis=dict(
                #title='Historical Daily Closing Price',
                titlefont=dict(
                    color='rgb(148, 103, 189)'
                ),
                tickfont=dict(
                    color='rgb(148, 103, 189)'
                ),
                domain = [0, .2],
                showticklabels = False
            ),
            yaxis2=dict(
                #title='Historical Daily Volume',

                domain = [0.2,0.8],

            ),
            margin = dict(t=40,b=40,r=40,l=40
            ),
            legend = dict( orientation = 'h', y=0.9, yanchor='bottom')

        )
    }

    # fig.append_trace({'x':graphDate,'y':graphVolume,'type':'bar','name':'Volume'},2,1)
    # fig['layout'].update(title='Graph of '+in_data)
    # return fig

@app.callback(
        Output('title', 'children'),
        [Input(component_id='crypto-type', component_property = 'value')]
        )
def update_title(dropdown_value):
    return (dropdown_value) + ' Graph'

if __name__ == "__main__":
    app.run_server(debug=True)
