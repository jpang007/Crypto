from dash.dependencies import Input, Output
import dash
from app import app

import requests
import json
import numpy
import plotly.graph_objs as go
from datetime import datetime
import plotly.tools as tls
#handles all calculations and callbacks
#calculates average gain and loss over a period (usually 14)
def calcDailyGains(ClosingPrice, RSIPeriod):
    AverageGain = []
    AverageLoss = []
    CurrentChange = 0
    for i in range(0,RSIPeriod):
        Change = ClosingPrice[i + 1] - ClosingPrice[i]
        if Change > 0:
            AverageGain.append(Change)
        else:
            AverageLoss.append(Change)
        #current gain
        if i == RSIPeriod - 1:
            if Change > 0:
                CurrentChange = Change
            else:
                CurrentChange = Change
    TotalAverageGain = (sum(AverageGain) / RSIPeriod)
    TotalAverageLoss = (sum(AverageLoss) / RSIPeriod)

    return TotalAverageGain, TotalAverageLoss, CurrentChange

#Formula to calculate RSI using average gain and loss
def calcRSI(TotalAverageGain, TotalAverageLoss, CurrentChange, RSIPeriod):
    CurrentGain = 0
    CurrentLoss = 0
    firstRSI = TotalAverageGain / abs(TotalAverageLoss)
    RSI = 100 - (100 / (1 + firstRSI))

    if CurrentChange > 0:
        CurrentGain = CurrentChange
    else:
        CurrentLoss = CurrentChange

    #smoothRSI
    smoothRSI = (((TotalAverageGain * (RSIPeriod - 1)) + CurrentGain) / RSIPeriod) / (((abs(TotalAverageLoss) * (RSIPeriod - 1)) + CurrentLoss) / RSIPeriod)
    finalRSI = 100 - (100 / (1 + smoothRSI))
    return finalRSI

#calculates simple moving average over a period (usually 20)
#returns values for middle upper and lower band
def calcSMA(ClosingPrice, BandPeriod):
    MiddleBand = numpy.mean(ClosingPrice)
    StandardDeviation = numpy.std(ClosingPrice)
    UpperBand = MiddleBand + (StandardDeviation * 2)
    LowerBand = MiddleBand - (StandardDeviation * 2)
    return LowerBand, MiddleBand, UpperBand

def getAPI(DaysToStore):
    #Get's the current price
    # currentprice = requests.get("https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,LTC&tsyms=USD&api_key=0bfac81ab05f7e572f8cc18a28a05c6c2f3665a10d17099efe1d7c2e3b3e0195")
    # pricedata = currentprice.json()
    # print (pricedata)

    bitcoinHistorical = requests.get("https://min-api.cryptocompare.com/data/histoday?fsym=BTC&tsym=USD&limit=" + str(DaysToStore) + "&api_key=0bfac81ab05f7e572f8cc18a28a05c6c2f3665a10d17099efe1d7c2e3b3e0195")
    bitcoinHistoricalData = bitcoinHistorical.json()
    #print (bitcoinHistoricalData['Data'])
    return bitcoinHistoricalData

#init block
DaysToDisplay = 365
DaysToStore = DaysToDisplay + 20 #Must always be 20 days greater (for RSI) than DaysToDisplay
CurrentDay = DaysToStore
bitcoinHistoricalData = getAPI(DaysToStore)
RSIClosingPrice, BandClosingPrice, RSIValues, LowerBandValues, MiddleBandValues, UpperBandValues = ([] for i in range(6))
RSIPeriod = 14
BandPeriod = 20

#block for RSI calcuation
for i in range(0, DaysToDisplay):
    RSIClosingPrice = [] #reset the list
    for j in range(CurrentDay - RSIPeriod, CurrentDay + 1):
        RSIClosingPrice.append(bitcoinHistoricalData['Data'][j]['close'])
    TotalAverageGain, TotalAverageLoss, CurrentChange = calcDailyGains(RSIClosingPrice, RSIPeriod)
    finalRSI = calcRSI(TotalAverageGain, TotalAverageLoss, CurrentChange, RSIPeriod)
    RSIValues.insert(0,finalRSI)
    CurrentDay = CurrentDay - 1

print (RSIValues)
CurrentDay = DaysToStore
#block for bollinger band calculation
for i in range(0, DaysToDisplay):
    BandClosingPrice = [] #reset the list
    for i in range(CurrentDay - BandPeriod, CurrentDay + 1):
        #BandClosingPrice.append(bitcoinHistoricalData[i]['close'])
        BandClosingPrice.append(bitcoinHistoricalData['Data'][i]['close'])
    LowerBand, MiddleBand, UpperBand = calcSMA(BandClosingPrice, BandPeriod)
    LowerBandValues.insert(0,LowerBand)
    MiddleBandValues.insert(0,MiddleBand)
    UpperBandValues.insert(0,UpperBand)
    CurrentDay = CurrentDay - 1

#print (LowerBandValues, MiddleBandValues, UpperBandValues)

#Dash Graphing
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

INCREASING_COLOR = '#17BECF'
DECREASING_COLOR = '#7F7F7F'

graphOpen, graphClose, graphHigh, graphLow, graphDate, graphVolume, graphRSI, graphBand = ([] for i in range(8))
for i in range(DaysToStore - DaysToDisplay + 1, DaysToStore):
    graphOpen.append(bitcoinHistoricalData['Data'][i]['open'])
    graphClose.append(bitcoinHistoricalData['Data'][i]['close'])
    graphHigh.append(bitcoinHistoricalData['Data'][i]['high'])
    graphLow.append(bitcoinHistoricalData['Data'][i]['low'])
    graphDate.append(datetime.utcfromtimestamp(bitcoinHistoricalData['Data'][i]['time']).strftime('%Y-%m-%d %H:%M:%S'))
    graphVolume.append(bitcoinHistoricalData['Data'][i]['volumeto'])
    # graphOpen.append(bitcoinHistoricalData[i]['open'])
    # graphClose.append(bitcoinHistoricalData[i]['close'])
    # graphHigh.append(bitcoinHistoricalData[i]['high'])
    # graphLow.append(bitcoinHistoricalData[i]['close'])
    # graphDate.append(datetime.utcfromtimestamp(bitcoinHistoricalData[i]['time']).strftime('%Y-%m-%d %H:%M:%S'))
    # graphVolume.append(bitcoinHistoricalData[i]['volumeto'])

# print graphDate
# print min(graphDate)[0:10]
# print datetime.strptime(min(graphDate)[0:10], '%Y-%m-%d')
# print max(graphDate)


#Callback for crypto overall graph
@app.callback(
        dash.dependencies.Output('bitcoin-graph', 'figure'),
        [dash.dependencies.Input(component_id='crypto-type', component_property = 'value')]
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
        name = 'Daily price',
        increasing = dict( line = dict( color = INCREASING_COLOR ) ),
        decreasing = dict( line = dict( color = DECREASING_COLOR ) ),
        ))

    #Volume
    colors = []
    for i in range(len(graphClose)):
        if i != 0:
            if graphClose[i] > graphClose[i-1]:
                colors.append(INCREASING_COLOR)
            else:
                colors.append(DECREASING_COLOR)
        else:
            colors.append(DECREASING_COLOR)
    traces.append(go.Bar(
        x=graphDate,
        y=graphVolume,
        yaxis='y',
        name = 'Volume',
        marker = dict(color=colors)
    ))
    #Upper Band
    traces.append(go.Scatter(
        x=graphDate,
        y=UpperBandValues,
        yaxis='y2',
        line=dict(
            color = 'rgb(173,216,230)',
            width = 1
        ),
        hoverinfo='none',
        legendgroup='Bollinger Bands',
        name='Bollinger Bands'
        )
    )

    traces.append(go.Scatter(
        x=graphDate,
        y=LowerBandValues,
        yaxis='y2',
        line=dict(
            color = 'rgb(173,216,230)',
            width = 1
        ),
        hoverinfo='none',
        legendgroup='Bollinger Bands',
        showlegend= False
        )
    )

    traces.append(go.Scatter(
        x=graphDate,
        y=MiddleBandValues,
        yaxis='y2',
        line=dict(
            color = 'rgb(139,0,0)',
            width = 1
        ),
        hoverinfo='none',
        legendgroup='Simple Moving Average',
        name = 'Simple Moving Average'
        )
    )


    return {
        'data': traces,
        'layout': go.Layout(
            title = (crypto_value) + ' Graph',
            xaxis = dict(
            #     rangeselector=dict(
            #         buttons=list([
            #             dict(count=7,
            #                  label='1w',
            #                  step='day',
            #                  stepmode='backward'),
            #             dict(count=1, ##can they fix this already??!?
            #                  label='1m',
            #                  step='month',
            #                  stepmode='backward'),
            #             dict(count=3,
            #                 label='3m',
            #                 step='month',
            #                 stepmode='todate'),
            #             dict(count=6,
            #                 label='6m',
            #                 step='month',
            #                 stepmode='backward'),
            #             dict(step='all')
            #         ])
            # ),
        rangeslider=dict(
            visible = False
        ),
        type='date'
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
                tickmode = 'auto'
            ),
            margin = dict(t=40,b=40,r=40,l=40
            ),
            height = 800,
            legend = dict( orientation = 'h', y=0.9, yanchor='bottom')

        )
    }
#callback updates RSI graph
@app.callback(
        dash.dependencies.Output('rsi-graph', 'figure'),
        [dash.dependencies.Input(component_id='crypto-type', component_property = 'value')]
)
def rsi_graph(crypto_value):
        traces2 = []
        traces2.append(go.Scatter(
            x=graphDate,
            y=RSIValues,
            line=dict(
                color = INCREASING_COLOR
            )
        ))
        return {
            'data': traces2,
            'layout': go.Layout(
            title = (crypto_value) + ' RSI Graph',
            xaxis = dict(
                rangeslider = dict( visible = False ),
            ),
            yaxis=dict(
                tickfont=dict(
                    color='rgb(148, 103, 189)'
                ),
                range = [0,100]
            ),
            margin = dict(t=40,b=40,r=40,l=40
            ),
            shapes=[
                    dict(
                    type='line',
                    x0= datetime.strptime(min(graphDate)[0:10], '%Y-%m-%d'),
                    x1= datetime.strptime(max(graphDate)[0:10], '%Y-%m-%d'),
                    y0= 70,
                    y1= 70,
                    line=dict(color= 'rgb(218,112,214)', dash='dot', width=1)
                    ),
                    dict(
                    type='line',
                    x0= datetime.strptime(min(graphDate)[0:10], '%Y-%m-%d'),
                    x1= datetime.strptime(max(graphDate)[0:10], '%Y-%m-%d'),
                    y0= 30,
                    y1= 30,
                    line=dict(color= 'rgb(218,112,214)', dash='dot', width=1)
                    ),
            ],
            legend = dict( orientation = 'h', y=0.9, yanchor='bottom')
            )
        }

@app.callback(
        Output('title', 'children'),
        [Input(component_id='crypto-type', component_property = 'value')]
        )
def update_title(dropdown_value):
    return (dropdown_value) + ' Graph'

@app.callback(dash.dependencies.Output('page-2-content', 'children'),
              [dash.dependencies.Input('page-2-radios', 'value')])
def page_2_radios(value):
    return 'You have selected "{}"'.format(value)
