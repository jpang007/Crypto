# -*- coding: utf-8 -*-
import requests
import json
import numpy
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from datetime import datetime

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
    print (RSI)

    if CurrentChange > 0:
        CurrentGain = CurrentChange
    else:
        CurrentLoss = CurrentChange

    #smoothRSI
    smoothRSI = (((TotalAverageGain * (RSIPeriod - 1)) + CurrentGain) / RSIPeriod) / (((abs(TotalAverageLoss) * (RSIPeriod - 1)) + CurrentLoss) / RSIPeriod)
    finalRSI = 100 - (100 / (1 + smoothRSI))
    return finalRSI


#Get's the current price
currentprice = requests.get("https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC&tsyms=USD&api_key=0bfac81ab05f7e572f8cc18a28a05c6c2f3665a10d17099efe1d7c2e3b3e0195")
pricedata = currentprice.json()
print (pricedata)

bitcoinHistorical = requests.get("https://min-api.cryptocompare.com/data/histoday?fsym=BTC&tsym=USD&limit=20&api_key=0bfac81ab05f7e572f8cc18a28a05c6c2f3665a10d17099efe1d7c2e3b3e0195")
bitcoinHistoricalData = bitcoinHistorical.json()
#OpeningPrice = []
RSIClosingPrice = []
BandClosingPrice = []
RSIPeriod = 14
BandPeriod = 20
print (bitcoinHistoricalData['Data'])
for i in range(0 + 6, RSIPeriod + 6):
    #OpeningPrice.append(bitcoinHistoricalData['Data'][i]['open'])
    RSIClosingPrice.append(bitcoinHistoricalData['Data'][i]['close'])

for i in range(0, BandPeriod):
    #OpeningPrice.append(bitcoinHistoricalData['Data'][i]['open'])
    BandClosingPrice.append(bitcoinHistoricalData['Data'][i]['close'])

TotalAverageGain, TotalAverageLoss, CurrentChange = calcDailyGains(RSIClosingPrice, RSIPeriod)
finalRSI = calcRSI(TotalAverageGain, TotalAverageLoss, CurrentChange, RSIPeriod)
print (finalRSI)

LowerBand, MiddleBand, UpperBand = calcSMA(BandClosingPrice, BandPeriod)
print (LowerBand, MiddleBand, UpperBand)

#Dash Graphing
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
test = []
test1 = []
for i in range(0, BandPeriod):
    test.append(bitcoinHistoricalData['Data'][i]['close'])
    test1.append(datetime.utcfromtimestamp(bitcoinHistoricalData['Data'][i]['time']).strftime('%Y-%m-%d %H:%M:%S'))
app.layout = html.Div(children=[
    html.H1(
        children='Bitcoin Graph',
        style={
            'textAlign': 'center',
        }
    ),

    html.Div(children='Charting in style', style={
        'textAlign': 'center',
    }),

    dcc.Graph(
        id='bitcoin-graph',
        figure={
            'data': [
                go.Scatter(
                    x = test1,
                    y = test
                )
            ],
            'layout': go.Layout(
                xaxis={'title' : 'Date'},
                yaxis={'title': 'Price'}
            )
        }
    )
])


if __name__ == "__main__":
    app.run_server(debug=True)
