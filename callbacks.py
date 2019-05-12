from dash.dependencies import Input, Output, State
import dash
from app import app

import requests
import json
import numpy
import plotly.graph_objs as go
from datetime import datetime
import plotly.tools as tls
import pandas as pd

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

def calc12DayEMA(ClosingPrice, PreviousValue, Period):
    NextValue = (ClosingPrice * (float(2)/(Period+1))) + (PreviousValue *(1-(float(2)/(Period+1))))
    return NextValue

def getAPI(DaysToStore, symbol):
    #Get's the current price
    # currentprice = requests.get("https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,LTC&tsyms=USD&api_key=0bfac81ab05f7e572f8cc18a28a05c6c2f3665a10d17099efe1d7c2e3b3e0195")
    # pricedata = currentprice.json()
    # print (pricedata)

    cryptoHistorical = requests.get("https://min-api.cryptocompare.com/data/histoday?fsym=" + str(symbol) + "&tsym=USD&limit=" + str(DaysToStore) + "&api_key=0bfac81ab05f7e572f8cc18a28a05c6c2f3665a10d17099efe1d7c2e3b3e0195")
    cryptoHistoricalData = cryptoHistorical.json()
    return cryptoHistoricalData

def mainCalc(DaysToDisplay, DaysToStore, CurrentDay, cryptoHistoricalData, RSIPeriod, BandPeriod, MACDPeriod):
    RSIClosingPrice, BandClosingPrice, RSIValues, LowerBandValues, MiddleBandValues, UpperBandValues, Histogram, SignalList, MACDValues = ([] for i in range(9))
    #block for RSI calcuation
    for i in range(DaysToDisplay):
        RSIClosingPrice = [] #reset the list
        for j in range(CurrentDay - RSIPeriod, CurrentDay + 1):
            RSIClosingPrice.append(cryptoHistoricalData['Data'][j]['close'])
        TotalAverageGain, TotalAverageLoss, CurrentChange = calcDailyGains(RSIClosingPrice, RSIPeriod)
        finalRSI = calcRSI(TotalAverageGain, TotalAverageLoss, CurrentChange, RSIPeriod)
        RSIValues.append(finalRSI)
        CurrentDay = CurrentDay - 1

    #print (RSIValues)
    CurrentDay = DaysToStore
    #block for bollinger band calculation
    for i in range(DaysToDisplay):
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

    CurrentDay = 0
    EndDay = 12
    #block for MACD calculation
    EMA12DayCalc = []
    EMA12DayList = []
    EMA26DayList = []
    for i in range(CurrentDay, EndDay):
        EMA12DayCalc.append(cryptoHistoricalData['Data'][i]['close'])
    EMA12DayValue = numpy.mean(EMA12DayCalc)
    EMA12DayList.append(EMA12DayValue)

    for i in range(EndDay, DaysToStore): #Calculate for all values
        #Calculate all EMA 12 Day values
        EMA12ClosingPrice = (cryptoHistoricalData['Data'][EndDay]['close'])

        EMA12DayValue = calc12DayEMA(EMA12ClosingPrice,EMA12DayValue, 12)
        EMA12DayList.append(EMA12DayValue)
        EndDay = EndDay + 1

    #Calculate 26 Day EMA
    EMA26DayCalc = []
    CurrentDay = 0
    EndDay = 26
    for i in range(CurrentDay, EndDay):
        EMA26DayCalc.append(cryptoHistoricalData['Data'][i]['close'])
    EMA26DayValue = numpy.mean(EMA26DayCalc)
    EMA26DayList.append(EMA26DayValue)

    for i in range(EndDay, DaysToStore):
        EMA26ClosingPrice = (cryptoHistoricalData['Data'][EndDay]['close'])

        EMA26DayValue = calc12DayEMA(EMA26ClosingPrice,EMA26DayValue, 26)
        EMA26DayList.append(EMA26DayValue)
        EndDay = EndDay + 1

    del EMA12DayList[:14]

    for i in range(len(EMA26DayList)): #lists will always be the same length after trimming
        MACDValues.append(EMA12DayList[i] - EMA26DayList[i])

    CurrentDay = 0
    EndDay = 9
    SignalValue = numpy.mean(MACDValues[:EndDay])
    for i in range(EndDay - 1):
        SignalList.append(None)
        Histogram.append(None)

    SignalList.append(SignalValue)
    for i in range(EndDay,len(MACDValues)):
        SignalValue = calc12DayEMA(MACDValues[i], SignalValue, 9)
        SignalList.append(SignalValue)
    for i in range(len(SignalList)):
        if SignalList[i] != None:
            Histogram.append(MACDValues[i] - SignalList[i])
    # MACD = calcEMA(MACDValuesToCalc, MACDPeriod)


    graphOpen, graphClose, graphHigh, graphLow, graphDate, graphVolume, graphRSI, graphBand = ([] for i in range(8))
    for i in range(DaysToStore - DaysToDisplay, DaysToStore):
        graphOpen.append(cryptoHistoricalData['Data'][i]['open'])
        graphClose.append(cryptoHistoricalData['Data'][i]['close'])
        graphHigh.append(cryptoHistoricalData['Data'][i]['high'])
        graphLow.append(cryptoHistoricalData['Data'][i]['low'])
        graphDate.append(datetime.utcfromtimestamp(cryptoHistoricalData['Data'][i]['time']).strftime('%Y-%m-%d %H:%M:%S'))
        graphVolume.append(cryptoHistoricalData['Data'][i]['volumeto'])

    return RSIValues, LowerBandValues, MiddleBandValues, UpperBandValues, Histogram, SignalList, MACDValues, graphOpen, graphClose, graphHigh, graphLow, graphDate, graphVolume

def whichData(btcHistoricalData, ethHistoricalData, ltcHistoricalData, symbol):
    if (symbol == "BTC"):
        return btcHistoricalData
    if (symbol == "ETH"):
        return ethHistoricalData
    if (symbol == "LTC"):
        return ltcHistoricalData

#init block
DaysToDisplay = 365
DaysToStore = DaysToDisplay + 26 #Must always be 20 days greater (for RSI) than DaysToDisplay
CurrentDay = DaysToStore
btcHistoricalData = getAPI(DaysToStore, "BTC")
ethHistoricalData = getAPI(DaysToStore, "ETH")
ltcHistoricalData = getAPI(DaysToStore, "LTC")
RSIPeriod = 14
BandPeriod = 20
MACDPeriod = 26

#Dash Graphing
colors = {
    'background': '#D3D3D3',
    'text': '#7FDBFF'
}

INCREASING_COLOR = '#228B22'
DECREASING_COLOR = '#bf0000'
RSI_COLOR = '#17BECF'

#Callback for crypto overall graph
@app.callback(
        [Output('bitcoin-graph', 'figure'), Output('graphRangePercentage', 'children'), Output('graphRangePercentage', 'style')],
        [   Input(component_id='bitcoinImg', component_property = 'n_clicks_timestamp'),
            Input(component_id='litecoinImg', component_property = 'n_clicks_timestamp'),
            Input(component_id='ethereumImg', component_property = 'n_clicks_timestamp'),
            Input('my-date-picker-range', 'start_date'),
            Input('my-date-picker-range', 'end_date'),
            Input('btn-1', 'n_clicks_timestamp'),
            Input('btn-2', 'n_clicks_timestamp'),
            Input('btn-3', 'n_clicks_timestamp'),
            Input('btn-4', 'n_clicks_timestamp'),
            Input('techIndicators', 'values'),
            ]
        )
def update_graph(bitcoin, litecoin, ethereum, startDate, endDate, oneMonth, threeMonth, sixMonth, resetGraph, displayGraph):
    #TODO: Need to by able to change date either passed in through button click or the date picker
    if (oneMonth == None):
        oneMonth = 0
    if (threeMonth == None):
        threeMonth = 0
    if (sixMonth == None):
        sixMonth = 0
    if (resetGraph == None):
        resetGraph = 0
    if (bitcoin == None):
        bitcoin = 0
    if (litecoin == None):
        litecoin = 0
    if (ethereum == None):
        ethereum = 0


    possibleButtons = dict()
    possibleButtons.update({'bitcoin':bitcoin, 'litecoin':litecoin, 'ethereum':ethereum})

    buttonPressed = max(possibleButtons, key=possibleButtons.get)

    if (buttonPressed == "bitcoin"):
        crypto_value = "BTC"
    elif (buttonPressed == "litecoin"):
        crypto_value = "LTC"
    elif (buttonPressed == "ethereum"):
        crypto_value = "ETH"

    if (bitcoin == 0 and litecoin == 0 and ethereum == 0):
        crypto_value = 'BTC'


    cryptoHistoricalData = whichData(btcHistoricalData, ethHistoricalData, ltcHistoricalData, crypto_value) #changes value without having to do API recalls
    RSIValues, LowerBandValues, MiddleBandValues, UpperBandValues, Histogram, SignalList, MACDValues, graphOpen, graphClose, graphHigh, graphLow, graphDate, graphVolume = mainCalc(DaysToDisplay, DaysToStore, CurrentDay, cryptoHistoricalData, RSIPeriod, BandPeriod, MACDPeriod)
    traces = []

    originalGraphDate = graphDate
    originalGraphLower = LowerBandValues
    originalGraphMiddle = MiddleBandValues
    originalGraphUpper = UpperBandValues
    originalGraphOpen = graphOpen
    originalGraphClose = graphClose
    originalGraphHigh = graphHigh
    originalGraphLow = graphLow
    originalGraphVolume = graphVolume

    #code to get most recent button press
    possibleButtons = dict()
    possibleButtons.update({'oneMonth':oneMonth, 'threeMonth':threeMonth, 'sixMonth':sixMonth, 'resetGraph':resetGraph})

    buttonPressed = max(possibleButtons, key=possibleButtons.get)
    buttonPressedValue = possibleButtons.get(buttonPressed)

    if (buttonPressedValue != 0):
        if (buttonPressed == 'oneMonth'):
            graphDate = graphDate[-30:]
            LowerBandValues = LowerBandValues[-30:]
            MiddleBandValues = MiddleBandValues[-30:]
            UpperBandValues = UpperBandValues[-30:]
            graphOpen = graphOpen[-30:]
            graphClose = graphClose[-30:]
            graphHigh = graphHigh[-30:]
            graphLow = graphLow[-30:]
            graphVolume = graphVolume[-30:]

        if (buttonPressed == 'threeMonth'):
            graphDate = graphDate[-90:]
            LowerBandValues = LowerBandValues[-90:]
            MiddleBandValues = MiddleBandValues[-90:]
            UpperBandValues = UpperBandValues[-90:]
            graphOpen = graphOpen[-90:]
            graphClose = graphClose[-90:]
            graphHigh = graphHigh[-90:]
            graphLow = graphLow[-90:]
            graphVolume = graphVolume[-90:]

        if (buttonPressed == 'sixMonth'):
            graphDate = graphDate[-180:]
            LowerBandValues = LowerBandValues[-180:]
            MiddleBandValues = MiddleBandValues[-180:]
            UpperBandValues = UpperBandValues[-180:]
            graphOpen = graphOpen[-180:]
            graphClose = graphClose[-180:]
            graphHigh = graphHigh[-180:]
            graphLow = graphLow[-180:]
            graphVolume = graphVolume[-180:]

    if (startDate != None and endDate != None):
        graphDate = originalGraphDate
        LowerBandValues = originalGraphLower
        MiddleBandValues = originalGraphMiddle
        UpperBandValues = originalGraphUpper
        graphOpen = originalGraphOpen
        graphClose = originalGraphClose
        graphHigh = originalGraphHigh
        graphLow = originalGraphLow
        graphVolume = originalGraphVolume
        startDatePosition = graphDate.index(str(datetime.strptime(startDate, '%Y-%m-%d')))
        endDatePosition = graphDate.index(str(datetime.strptime(endDate, '%Y-%m-%d'))) + 1
        graphDate = graphDate[startDatePosition:endDatePosition]
        LowerBandValues = LowerBandValues[startDatePosition:endDatePosition]
        MiddleBandValues = MiddleBandValues[startDatePosition:endDatePosition]
        UpperBandValues = UpperBandValues[startDatePosition:endDatePosition]
        graphOpen = graphOpen[startDatePosition:endDatePosition]
        graphClose = graphClose[startDatePosition:endDatePosition]
        graphHigh = graphHigh[startDatePosition:endDatePosition]
        graphLow = graphLow[startDatePosition:endDatePosition]
        graphVolume = graphVolume[startDatePosition:endDatePosition]

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
    if 'BB' in displayGraph:
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

    figure = go.Figure(
        data = traces,
        layout = go.Layout(
            title = (crypto_value) + ' Graph',
            xaxis = dict(
                rangeslider=dict(
                    visible = False
                ),
            type='date',
            showspikes= True,
            spikemode='across',
            spikesnap='cursor'
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
    )

    startGraphGains = graphClose[0]
    endGraphGains = graphClose[-1]
    graphGains = round((((endGraphGains - startGraphGains) / startGraphGains) * 100), 2)
    if (graphGains < 0):
        graphGainsColor = DECREASING_COLOR
    else:
        graphGainsColor = INCREASING_COLOR

    return figure, str(graphGains) + "%", {'color': graphGainsColor}

#callback updates RSI graph
@app.callback(
        Output('rsi-graph', 'figure'),
        [   Input(component_id='bitcoinImg', component_property = 'n_clicks_timestamp'),
            Input(component_id='litecoinImg', component_property = 'n_clicks_timestamp'),
            Input(component_id='ethereumImg', component_property = 'n_clicks_timestamp'),
            Input('my-date-picker-range', 'start_date'),
            Input('my-date-picker-range', 'end_date'),
            Input('btn-1', 'n_clicks_timestamp'),
            Input('btn-2', 'n_clicks_timestamp'),
            Input('btn-3', 'n_clicks_timestamp'),
            Input('btn-4', 'n_clicks_timestamp'),
            Input('techIndicators', 'values')
            ]
)
def rsi_graph(bitcoin, litecoin, ethereum, startDate, endDate, oneMonth, threeMonth, sixMonth, resetGraph, tech):
    if (oneMonth == None):
        oneMonth = 0
    if (threeMonth == None):
        threeMonth = 0
    if (sixMonth == None):
        sixMonth = 0
    if (resetGraph == None):
        resetGraph = 0
    if (bitcoin == None):
        bitcoin = 0
    if (litecoin == None):
        litecoin = 0
    if (ethereum == None):
        ethereum = 0

    possibleButtons = dict()
    possibleButtons.update({'bitcoin':bitcoin, 'litecoin':litecoin, 'ethereum':ethereum})

    buttonPressed = max(possibleButtons, key=possibleButtons.get)

    if (buttonPressed == "bitcoin"):
        crypto_value = "BTC"
    elif (buttonPressed == "litecoin"):
        crypto_value = "LTC"
    elif (buttonPressed == "ethereum"):
        crypto_value = "ETH"

    if (bitcoin == 0 and litecoin == 0 and ethereum == 0):
        crypto_value = 'BTC'

    cryptoHistoricalData = whichData(btcHistoricalData, ethHistoricalData, ltcHistoricalData, crypto_value) #changes value without having to do API recalls
    RSIValues, LowerBandValues, MiddleBandValues, UpperBandValues, Histogram, SignalList, MACDValues, graphOpen, graphClose, graphHigh, graphLow, graphDate, graphVolume = mainCalc(DaysToDisplay, DaysToStore, CurrentDay, cryptoHistoricalData, RSIPeriod, BandPeriod, MACDPeriod)
    RSIValues = RSIValues[::-1]

    originalGraphDate = graphDate
    originalGraphRSI = RSIValues

    traces2 = []

    possibleButtons = dict()
    possibleButtons.update({'oneMonth':oneMonth, 'threeMonth':threeMonth, 'sixMonth':sixMonth, 'resetGraph':resetGraph})

    buttonPressed = max(possibleButtons, key=possibleButtons.get)
    buttonPressedValue = possibleButtons.get(buttonPressed)

    if (buttonPressedValue != 0):
        if (buttonPressed == 'oneMonth'):
            graphDate = graphDate[-30:]
            RSIValues = RSIValues[-30:]

        if (buttonPressed == 'threeMonth'):
            graphDate = graphDate[-90:]
            RSIValues = RSIValues[-90:]

        if (buttonPressed == 'sixMonth'):
            graphDate = graphDate[-180:]
            RSIValues = RSIValues[-180:]

    if (startDate != None and endDate != None):
        graphDate = originalGraphDate
        RSIValues = originalGraphRSI
        startDatePosition = graphDate.index(str(datetime.strptime(startDate, '%Y-%m-%d')))
        endDatePosition = graphDate.index(str(datetime.strptime(endDate, '%Y-%m-%d'))) + 1
        graphDate = graphDate[startDatePosition:endDatePosition]
        RSIValues = RSIValues[startDatePosition:endDatePosition]

    traces2.append(go.Scatter(
        x=graphDate,
        y=RSIValues,
        name = 'RSI Value',
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
        height = 200,
        plot_bgcolor = '#D3D3D3'
        )
    }

#callback updates MACD graph
@app.callback(
        Output('macd-graph', 'figure'),
        [   Input(component_id='bitcoinImg', component_property = 'n_clicks_timestamp'),
            Input(component_id='litecoinImg', component_property = 'n_clicks_timestamp'),
            Input(component_id='ethereumImg', component_property = 'n_clicks_timestamp'),
            Input('my-date-picker-range', 'start_date'),
            Input('my-date-picker-range', 'end_date'),
            Input('btn-1', 'n_clicks_timestamp'),
            Input('btn-2', 'n_clicks_timestamp'),
            Input('btn-3', 'n_clicks_timestamp'),
            Input('btn-4', 'n_clicks_timestamp'),
            Input('techIndicators', 'values')
            ]
)
def macd_graph(bitcoin, litecoin, ethereum, startDate, endDate, oneMonth, threeMonth, sixMonth, resetGraph, tech):
    if (oneMonth == None):
        oneMonth = 0
    if (threeMonth == None):
        threeMonth = 0
    if (sixMonth == None):
        sixMonth = 0
    if (resetGraph == None):
        resetGraph = 0
    if (bitcoin == None):
        bitcoin = 0
    if (litecoin == None):
        litecoin = 0
    if (ethereum == None):
        ethereum = 0

    possibleButtons = dict()
    possibleButtons.update({'bitcoin':bitcoin, 'litecoin':litecoin, 'ethereum':ethereum})

    buttonPressed = max(possibleButtons, key=possibleButtons.get)

    if (buttonPressed == "bitcoin"):
        crypto_value = "BTC"
    elif (buttonPressed == "litecoin"):
        crypto_value = "LTC"
    elif (buttonPressed == "ethereum"):
        crypto_value = "ETH"

    if (bitcoin == 0 and litecoin == 0 and ethereum == 0):
        crypto_value = 'BTC'

    cryptoHistoricalData = whichData(btcHistoricalData, ethHistoricalData, ltcHistoricalData, crypto_value) #changes value without having to do API recalls
    RSIValues, LowerBandValues, MiddleBandValues, UpperBandValues, Histogram, SignalList, MACDList, graphOpen, graphClose, graphHigh, graphLow, graphDate, graphVolume = mainCalc(DaysToDisplay, DaysToStore, CurrentDay, cryptoHistoricalData, RSIPeriod, BandPeriod, MACDPeriod)

    originalGraphDate = graphDate
    originalGraphRSI = RSIValues

    traces3 = []

    possibleButtons = dict()
    possibleButtons.update({'oneMonth':oneMonth, 'threeMonth':threeMonth, 'sixMonth':sixMonth, 'resetGraph':resetGraph})

    buttonPressed = max(possibleButtons, key=possibleButtons.get)
    buttonPressedValue = possibleButtons.get(buttonPressed)

    if (buttonPressedValue != 0):
        if (buttonPressed == 'oneMonth'):
            graphDate = graphDate[-30:]
            Histogram = Histogram[-30:]
            SignalList = SignalList[-30:]
            MACDList = MACDList[-30:]

        if (buttonPressed == 'threeMonth'):
            graphDate = graphDate[-90:]
            Histogram = Histogram[-90:]
            SignalList = SignalList[-90:]
            MACDList = MACDList[-90:]

        if (buttonPressed == 'sixMonth'):
            graphDate = graphDate[-180:]
            Histogram = Histogram[-180:]
            SignalList = SignalList[-180:]
            MACDList = MACDList[-180:]

    if (startDate != None and endDate != None):
        graphDate = originalGraphDate
        RSIValues = originalGraphRSI
        startDatePosition = graphDate.index(str(datetime.strptime(startDate, '%Y-%m-%d')))
        endDatePosition = graphDate.index(str(datetime.strptime(endDate, '%Y-%m-%d'))) + 1
        graphDate = graphDate[startDatePosition:endDatePosition]
        Histogram = Histogram[startDatePosition:endDatePosition]
        SignalList = SignalList[startDatePosition:endDatePosition]
        MACDList = MACDList[startDatePosition:endDatePosition]

    colors = []
    for i in range(len(Histogram)):
        if i != 0:
            SwitchedValue = False
            if Histogram[i] == None:
                Histogram[i] = 0
                SwitchedValue = True
            if Histogram[i] != None:
                if Histogram[i] > 0:
                    colors.append(INCREASING_COLOR)
                else:
                    colors.append(DECREASING_COLOR)
                if SwitchedValue == True:
                    Histogram[i] = None
        else:
            colors.append(DECREASING_COLOR)

    traces3.append(go.Bar(
        x=graphDate,
        y=Histogram,
        yaxis='y',
        name = 'Histogram',
        marker = dict(color=colors)
    ))

    traces3.append(go.Scatter(
        x=graphDate,
        y=MACDList,
        name = 'MACD Line',
        line=dict(
            color = RSI_COLOR
        )
    ))

    traces3.append(go.Scatter(
        x=graphDate,
        y=SignalList,
        name = 'Signal Line',
        line=dict(
            color = 'crimson'
        )
    ))

    return {
        'data': traces3,
        'layout': go.Layout(
        title = (crypto_value) + ' MACD Graph',
        xaxis = dict(
            rangeslider = dict( visible = False ),
        ),
        yaxis=dict(
            tickfont=dict(
                color='rgb(0, 0, 0)' #black
            )
        ),
        margin = dict(t=40,b=40,r=40,l=40
        ),
        legend = dict( orientation = 'h', y=0.9, yanchor='bottom'),
        paper_bgcolor = '#D3D3D3',
        plot_bgcolor = '#D3D3D3',
        height = 350
        )
    }

@app.callback(
        Output('my-date-picker-range', 'end_date'),
        [dash.dependencies.Input('btn-1', 'n_clicks'),
        dash.dependencies.Input('btn-2', 'n_clicks'),
        dash.dependencies.Input('btn-3', 'n_clicks'),
        dash.dependencies.Input('btn-4', 'n_clicks')]
        )
def reset_datepicker(oneMonth, threeMonth, sixMonth, resetDate):
    if (oneMonth is not None) and (oneMonth > 0):
        return None
    if (threeMonth is not None) and (threeMonth > 0):
        return None
    if (sixMonth is not None) and (sixMonth > 0):
        return None
    if (resetDate is not None) and (resetDate > 0):
        return None


@app.callback(
        Output('my-date-picker-range', 'start_date'),
        [dash.dependencies.Input('btn-1', 'n_clicks'),
        dash.dependencies.Input('btn-2', 'n_clicks'),
        dash.dependencies.Input('btn-3', 'n_clicks'),
        dash.dependencies.Input('btn-4', 'n_clicks')]
        )
def reset_datepicker(oneMonth, threeMonth, sixMonth, resetDate):
    if (oneMonth is not None) and (oneMonth > 0):
        return None
    if (threeMonth is not None) and (threeMonth > 0):
        return None
    if (sixMonth is not None) and (sixMonth > 0):
        return None
    if (resetDate is not None) and (resetDate > 0):
        return None

@app.callback(Output('rsi-container', 'style'),
    [dash.dependencies.Input('techIndicators', 'values')])
def hide_graph(displayGraph):
    if 'RSI' in displayGraph:
        return {'display':'block'}
    else:
        return {'display':'none'}

@app.callback(Output('macd-container', 'style'),
    [dash.dependencies.Input('techIndicators', 'values')])
def hide_graph(displayGraph):
    if 'MAC' in displayGraph:
        return {'display':'block'}
    else:
        return {'display':'none'}

#literally the stupidest way to trade
def RSISignal(RSIValues, graphDate, graphClose, testdollars):
    btcHoldings = 0
    amountSold = btcHoldings

    dateList, priceList, tradeList, totalReturn = ([] for i in range(4))
    for counter, value in enumerate(RSIValues):
        convert = 0
        if (int(value) >= 80): #sell indicator
            if (btcHoldings > 0):
                dateList.append(graphDate[counter])
                priceList.append(graphClose[counter])
                tradeList.append("Sell")
                convert = btcHoldings * graphClose[counter]
                totalReturn.append(convert)
            testdollars += btcHoldings * graphClose[counter]
            btcHoldings = 0#btcHoldings - amountSold

        elif (int(value) <= 20): #buy indicator
            if (testdollars > 0):
                dateList.append(graphDate[counter])
                priceList.append(graphClose[counter])
                tradeList.append("Buy")
                totalReturn.append(testdollars)
            btcHoldings += testdollars / graphClose[counter]
            testdollars = 0 #testdollars - dollarSold
    #if holdings are in bitcoin cash out to dollars to display current value
    if (btcHoldings > 0):
        testdollars = graphClose[-1] * btcHoldings
        btcHoldings = 0

    return dateList, priceList, tradeList, totalReturn, testdollars

def bollingerBand(UpperBandValues, LowerBandValues, graphDate, graphClose, testdollars):
    btcHoldings = 0
    amountSold = btcHoldings

    dateList, priceList, tradeList, totalReturn = ([] for i in range(4))
    for counter, value in enumerate(graphClose):
        convert = 0
        if (int(value) > UpperBandValues[counter]): #sell indicator
            if (btcHoldings > 0):
                dateList.append(graphDate[counter])
                priceList.append(graphClose[counter])
                tradeList.append("Sell")
                convert = btcHoldings * graphClose[counter]
                totalReturn.append(convert)
            testdollars += btcHoldings * graphClose[counter]
            btcHoldings = 0#btcHoldings - amountSold
        elif (int(value) < LowerBandValues[counter]):
            if (testdollars > 0):
                dateList.append(graphDate[counter])
                priceList.append(graphClose[counter])
                tradeList.append("Buy")
                totalReturn.append(testdollars)
            btcHoldings += testdollars / graphClose[counter]
            testdollars = 0 #testdollars - dollarSold

    if (btcHoldings > 0):
        testdollars = graphClose[-1] * btcHoldings
        btcHoldings = 0

    return dateList, priceList, tradeList, totalReturn, testdollars


@app.callback([Output('backtestPercent', 'children'), Output('backtestPercent', 'style'), Output('tradeTable', 'data'), Output('currentCoin', 'children')],
    [Input(component_id='radioItems1', component_property = 'value'),
    Input(component_id='radioItems2', component_property = 'value'),
    Input(component_id='input-1-submit', component_property = 'n_submit'),
    Input(component_id='input-1-submit', component_property = 'n_blur'),
    Input(component_id='bitcoinBacktestImg', component_property = 'n_clicks_timestamp'),
    Input(component_id='litecoinBacktestImg', component_property = 'n_clicks_timestamp'),
    Input(component_id='ethereumBacktestImg', component_property = 'n_clicks_timestamp')
    ],
    [State('input-1-submit', 'value')])
def calculateBacktestPercent(basic, advanced, dollarsSubmit, dollarsBlur, bitcoin, litecoin, ethereum, input1):
    if (bitcoin == None):
        bitcoin = 0
    if (litecoin == None):
        litecoin = 0
    if (ethereum == None):
        ethereum = 0

    tradeHistory = dict()
    masterlist = []

    testdollars = int(input1)

    possibleButtons = dict()
    possibleButtons.update({'bitcoin':bitcoin, 'litecoin':litecoin, 'ethereum':ethereum})

    buttonPressed = max(possibleButtons, key=possibleButtons.get)
    buttonPressedValue = possibleButtons.get(buttonPressed)

    if (buttonPressed == "bitcoin"):
        crypto_value = "BTC"
    elif (buttonPressed == "litecoin"):
        crypto_value = "LTC"
    elif (buttonPressed == "ethereum"):
        crypto_value = "ETH"

    if (bitcoin == 0 and litecoin == 0 and ethereum == 0):
        crypto_value = 'BTC'

    cryptoHistoricalData = whichData(btcHistoricalData, ethHistoricalData, ltcHistoricalData, crypto_value) #changes value without having to do API recalls
    RSIValues, LowerBandValues, MiddleBandValues, UpperBandValues, Histogram, SignalList, MACDList, graphOpen, graphClose, graphHigh, graphLow, graphDate, graphVolume = mainCalc(DaysToDisplay, DaysToStore, CurrentDay, cryptoHistoricalData, RSIPeriod, BandPeriod, MACDPeriod)
    RSIValues = RSIValues[::-1]
    print basic
    if (basic == "RSI"):
        dateList, priceList, tradeList, totalReturn, value = RSISignal(RSIValues, graphDate, graphClose, testdollars)
    elif (basic == "BB"):
        value = bollingerBand(UpperBandValues, LowerBandValues, graphDate, graphClose, testdollars)
    else:
        return str(0) + "%", {'color': '#000000'}, masterlist, crypto_value

    finalPercent = round((((value - testdollars) / testdollars) * 100), 2)
    if (finalPercent < 0):
        graphGainsColor = DECREASING_COLOR
    else:
        graphGainsColor = INCREASING_COLOR

    for counter, value in enumerate(dateList):
        splitValues = value.split()
        tradeHistory = dict({'Trade Number': counter + 1, 'Trade Date': splitValues[0], 'Decision': tradeList[counter], 'Price Filled': priceList[counter], 'Total Return': totalReturn[counter], 'Total Return Percent': round((((totalReturn[counter] - testdollars) / testdollars) * 100), 2)})
        masterlist.append(tradeHistory)

    return str(finalPercent) + "%", {'color': graphGainsColor}, masterlist, crypto_value
