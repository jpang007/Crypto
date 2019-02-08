# -*- coding: utf-8 -*-
import requests
import json
import numpy
import dash
import dash_core_components as dcc
import dash_html_components as html


from pprint import pprint

#calculates average gain and loss over a period (usually 14)
def calcDailyGains(ClosingPrice, Period):
    AverageGain = []
    AverageLoss = []
    CurrentChange = 0
    for i, j in enumerate(range(0,Period - 1)):
        Change = ClosingPrice[i + 1] - ClosingPrice[i]
        if Change > 0:
            AverageGain.append(Change)
        else:
            AverageLoss.append(Change)
        #current gain
        if j == Period - 2:
            if Change > 0:
                CurrentChange = Change
            else:
                CurrentChange = Change

    TotalAverageGain = (sum(AverageGain) / Period)
    TotalAverageLoss = (sum(AverageLoss) / Period)

    return TotalAverageGain, TotalAverageLoss, CurrentChange

#calculates simple moving average over a period (usually 20)
#returns values for middle upper and lower band
def calcSMA(ClosingPrice, Period):
    MiddleBand = (sum(ClosingPrice) / Period)
    StandardDeviation = numpy.std(ClosingPrice)
    UpperBand = MiddleBand + (StandardDeviation * 2)
    LowerBand = MiddleBand - (StandardDeviation * 2)
    return LowerBand, MiddleBand, UpperBand

#Formula to calculate RSI using average gain and loss
def calcRSI(TotalAverageGain, TotalAverageLoss, CurrentChange, Period):
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
    smoothRSI = (((TotalAverageGain * (Period - 1)) + CurrentGain) / Period) / (((abs(TotalAverageLoss) * (Period - 1)) + CurrentLoss) / Period)
    finalRSI = 100 - (100 / (1 + smoothRSI))
    return finalRSI


#Get's the current price
# currentprice = requests.get("https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,LTC&tsyms=USD&api_key=0bfac81ab05f7e572f8cc18a28a05c6c2f3665a10d17099efe1d7c2e3b3e0195")
# pricedata = currentprice.json()
# print (pricedata)

bitcoinHistorical = requests.get("https://min-api.cryptocompare.com/data/histoday?fsym=BTC&tsym=USD&limit=14&api_key=0bfac81ab05f7e572f8cc18a28a05c6c2f3665a10d17099efe1d7c2e3b3e0195")
bitcoinHistoricalData = bitcoinHistorical.json()
#OpeningPrice = []
ClosingPrice = []
Period = 14
for i in range(0, Period):
    #OpeningPrice.append(bitcoinHistoricalData['Data'][i]['open'])
    ClosingPrice.append(bitcoinHistoricalData['Data'][i]['close'])

TotalAverageGain, TotalAverageLoss, CurrentChange = calcDailyGains(ClosingPrice, Period)
finalRSI = calcRSI(TotalAverageGain, TotalAverageLoss, CurrentChange, Period)
print (finalRSI)
LowerBand, MiddleBand, UpperBand = calcSMA(ClosingPrice, Period)

#Dash Graphing
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for Python.
    '''),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
            ],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        }
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)
