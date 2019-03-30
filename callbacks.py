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

def getAPI(DaysToStore, symbol):
    #Get's the current price
    # currentprice = requests.get("https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,LTC&tsyms=USD&api_key=0bfac81ab05f7e572f8cc18a28a05c6c2f3665a10d17099efe1d7c2e3b3e0195")
    # pricedata = currentprice.json()
    # print (pricedata)

    cryptoHistorical = requests.get("https://min-api.cryptocompare.com/data/histoday?fsym=" + str(symbol) + "&tsym=USD&limit=" + str(DaysToStore) + "&api_key=0bfac81ab05f7e572f8cc18a28a05c6c2f3665a10d17099efe1d7c2e3b3e0195")
    cryptoHistoricalData = cryptoHistorical.json()
    return cryptoHistoricalData

def mainCalc(DaysToDisplay, DaysToStore, CurrentDay, cryptoHistoricalData, RSIPeriod, BandPeriod):
    RSIClosingPrice, BandClosingPrice, RSIValues, LowerBandValues, MiddleBandValues, UpperBandValues = ([] for i in range(6))
    #block for RSI calcuation
    for i in range(0, DaysToDisplay):
        RSIClosingPrice = [] #reset the list
        for j in range(CurrentDay - RSIPeriod, CurrentDay + 1):
            RSIClosingPrice.append(cryptoHistoricalData['Data'][j]['close'])
        TotalAverageGain, TotalAverageLoss, CurrentChange = calcDailyGains(RSIClosingPrice, RSIPeriod)
        finalRSI = calcRSI(TotalAverageGain, TotalAverageLoss, CurrentChange, RSIPeriod)
        RSIValues.insert(0,finalRSI)
        CurrentDay = CurrentDay - 1

    #print (RSIValues)
    CurrentDay = DaysToStore
    #block for bollinger band calculation
    for i in range(0, DaysToDisplay):
        BandClosingPrice = [] #reset the list
        for i in range(CurrentDay - BandPeriod, CurrentDay + 1):
            #BandClosingPrice.append(bitcoinHistoricalData[i]['close'])
            BandClosingPrice.append(cryptoHistoricalData['Data'][i]['close'])
        LowerBand, MiddleBand, UpperBand = calcSMA(BandClosingPrice, BandPeriod)
        LowerBandValues.insert(0,LowerBand)
        MiddleBandValues.insert(0,MiddleBand)
        UpperBandValues.insert(0,UpperBand)
        CurrentDay = CurrentDay - 1

    #print (LowerBandValues, MiddleBandValues, UpperBandValues)

    graphOpen, graphClose, graphHigh, graphLow, graphDate, graphVolume, graphRSI, graphBand = ([] for i in range(8))
    for i in range(DaysToStore - DaysToDisplay + 1, DaysToStore):
        graphOpen.append(cryptoHistoricalData['Data'][i]['open'])
        graphClose.append(cryptoHistoricalData['Data'][i]['close'])
        graphHigh.append(cryptoHistoricalData['Data'][i]['high'])
        graphLow.append(cryptoHistoricalData['Data'][i]['low'])
        graphDate.append(datetime.utcfromtimestamp(cryptoHistoricalData['Data'][i]['time']).strftime('%Y-%m-%d %H:%M:%S'))
        graphVolume.append(cryptoHistoricalData['Data'][i]['volumeto'])

    return RSIValues, LowerBandValues, MiddleBandValues, UpperBandValues, graphOpen, graphClose, graphHigh, graphLow, graphDate, graphVolume

def whichData(btcHistoricalData, ethHistoricalData, ltcHistoricalData, symbol):
    if (symbol == "BTC"):
        return btcHistoricalData
    if (symbol == "ETH"):
        return ethHistoricalData
    if (symbol == "LTC"):
        return ltcHistoricalData


#init block
DaysToDisplay = 367
DaysToStore = DaysToDisplay + 20 #Must always be 20 days greater (for RSI) than DaysToDisplay
CurrentDay = DaysToStore
btcHistoricalData = getAPI(DaysToStore, "BTC")
ethHistoricalData = getAPI(DaysToStore, "ETH")
ltcHistoricalData = getAPI(DaysToStore, "LTC")
RSIPeriod = 14
BandPeriod = 20

RSIValues, LowerBandValues, MiddleBandValues, UpperBandValues, graphOpen, graphClose, graphHigh, graphLow, graphDate, graphVolume = mainCalc(DaysToDisplay, DaysToStore, CurrentDay, btcHistoricalData, RSIPeriod, BandPeriod)

#Dash Graphing
colors = {
    'background': '#D3D3D3',
    'text': '#7FDBFF'
}

INCREASING_COLOR = '#54df1d'
DECREASING_COLOR = '#bf0000'
RSI_COLOR = '#17BECF'

#Callback for crypto overall graph
@app.callback(
        dash.dependencies.Output('bitcoin-graph', 'figure'),
        [   dash.dependencies.Input(component_id='crypto-type', component_property = 'value'),
            dash.dependencies.Input('my-date-picker-range', 'start_date'),
            dash.dependencies.Input('my-date-picker-range', 'end_date'),
            dash.dependencies.Input('btn-1', 'n_clicks_timestamp'),
            dash.dependencies.Input('btn-2', 'n_clicks_timestamp'),
            dash.dependencies.Input('btn-3', 'n_clicks_timestamp'),
            dash.dependencies.Input('btn-4', 'n_clicks_timestamp')
            ]
        )
def update_graph(crypto_value, startDate, endDate, oneMonth, threeMonth, sixMonth, resetGraph):
    #TODO: Need to by able to change date either passed in through button click or the date picker

    cryptoHistoricalData = whichData(btcHistoricalData, ethHistoricalData, ltcHistoricalData, crypto_value) #changes value without having to do API recalls
    RSIValues, LowerBandValues, MiddleBandValues, UpperBandValues, graphOpen, graphClose, graphHigh, graphLow, graphDate, graphVolume = mainCalc(DaysToDisplay, DaysToStore, CurrentDay, cryptoHistoricalData, RSIPeriod, BandPeriod)
    traces = []
    #code to get most recent button press
    possibleButtons = dict()
    possibleButtons.update({'oneMonth':oneMonth, 'threeMonth':threeMonth, 'sixMonth':sixMonth, 'resetGraph':resetGraph})

    buttonPressed = max(possibleButtons.items(), key=lambda i: i[1])
    if (buttonPressed[1] != None):
        #Code for changing the date interval
        originalGraphDate = graphDate

        if (buttonPressed[0] == 'oneMonth'):
            graphDate = graphDate[-30:]

        if (buttonPressed[0] == 'threeMonth'):
            graphDate = graphDate[-90:]

        if (buttonPressed[0] == 'sixMonth'):
            graphDate = graphDate[-180:]

        if (buttonPressed[0] == 'resetGraph'):
            graphDate = originalGraphDate

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
            color = RSI_COLOR,
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
            color = RSI_COLOR,
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
            legend = dict( orientation = 'h', y=0.9, yanchor='bottom'),
            paper_bgcolor = '#D3D3D3',
            plot_bgcolor = '#D3D3D3'


        )
    }
#callback updates RSI graph
@app.callback(
        dash.dependencies.Output('rsi-graph', 'figure'),
        [dash.dependencies.Input(component_id='crypto-type', component_property = 'value'),
            dash.dependencies.Input('my-date-picker-range', 'start_date'),
            dash.dependencies.Input('my-date-picker-range', 'end_date'),
            dash.dependencies.Input('btn-1', 'n_clicks_timestamp'),
            dash.dependencies.Input('btn-2', 'n_clicks_timestamp'),
            dash.dependencies.Input('btn-3', 'n_clicks_timestamp'),
            dash.dependencies.Input('btn-4', 'n_clicks_timestamp')]
)
def rsi_graph(crypto_value, startDate, endDate, oneMonth, threeMonth, sixMonth, resetGraph):
        cryptoHistoricalData = whichData(btcHistoricalData, ethHistoricalData, ltcHistoricalData, crypto_value) #changes value without having to do API recalls
        RSIValues, LowerBandValues, MiddleBandValues, UpperBandValues, graphOpen, graphClose, graphHigh, graphLow, graphDate, graphVolume = mainCalc(DaysToDisplay, DaysToStore, CurrentDay, cryptoHistoricalData, RSIPeriod, BandPeriod)
        traces2 = []

        possibleButtons = dict()
        possibleButtons.update({'oneMonth':oneMonth, 'threeMonth':threeMonth, 'sixMonth':sixMonth, 'resetGraph':resetGraph})

        buttonPressed = max(possibleButtons.items(), key=lambda i: i[1])
        if (buttonPressed[1] != None):
            #Code for changing the date interval
            originalGraphDate = graphDate

            if (buttonPressed[0] == 'oneMonth'):
                graphDate = graphDate[-30:]

            if (buttonPressed[0] == 'threeMonth'):
                graphDate = graphDate[-90:]

            if (buttonPressed[0] == 'sixMonth'):
                graphDate = graphDate[-180:]

            if (buttonPressed[0] == 'resetGraph'):
                graphDate = originalGraphDate

        traces2.append(go.Scatter(
            x=graphDate,
            y=RSIValues,
            line=dict(
                color = RSI_COLOR
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
                    color='rgb(0, 0, 0)' #black
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
                    line=dict(color= 'rgb(128,0,128)', dash='dot', width=1)
                    ),
                    dict(
                    type='line',
                    x0= datetime.strptime(min(graphDate)[0:10], '%Y-%m-%d'),
                    x1= datetime.strptime(max(graphDate)[0:10], '%Y-%m-%d'),
                    y0= 30,
                    y1= 30,
                    line=dict(color= 'rgb(128,0,128)', dash='dot', width=1)
                    ),
            ],
            legend = dict( orientation = 'h', y=0.9, yanchor='bottom'),
            paper_bgcolor = '#D3D3D3',
            plot_bgcolor = '#D3D3D3'
            )
        }

#TODO: I want to implement MACD, EMA crossover, RSI + Bollinger band strategy

@app.callback(
        Output('my-date-picker-range', 'end_date'),
        [dash.dependencies.Input('btn-5', 'n_clicks')]
        )
def reset_datepicker(resetDate):
    if (resetDate is not None) and (resetDate > 0):
        return None


@app.callback(
        Output('my-date-picker-range', 'start_date'),
        [dash.dependencies.Input('btn-5', 'n_clicks')]
        )
def reset_datepicker(resetDate):
    if (resetDate is not None) and (resetDate > 0):
        return None
