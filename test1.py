import requests
import json
import numpy
def getAPI(DaysToStore):
    #Get's the current price
    currentprice = requests.get("https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH,LTC&tsyms=USD&api_key=0bfac81ab05f7e572f8cc18a28a05c6c2f3665a10d17099efe1d7c2e3b3e0195")
    pricedata = currentprice.json()
    print (pricedata)

    bitcoinHistorical = requests.get("https://min-api.cryptocompare.com/data/histoday?fsym=BTC&tsym=USD&limit=" + str(DaysToStore) + "&api_key=0bfac81ab05f7e572f8cc18a28a05c6c2f3665a10d17099efe1d7c2e3b3e0195")
    bitcoinHistoricalData = bitcoinHistorical.json()
    #print (bitcoinHistoricalData['Data'])
    return bitcoinHistoricalData

#calculates average gain and loss over a period (usually 14)
def calcDailyGains(ClosingPrice, RSIPeriod):
    AverageGain = []
    AverageLoss = []
    CurrentChange = 0
    for i in range(0,RSIPeriod):
        Change = ClosingPrice[i + 1] - ClosingPrice[i]
        print Change
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
    print AverageGain
    print AverageLoss
    TotalAverageGain = (sum(AverageGain) / RSIPeriod)
    TotalAverageLoss = (sum(AverageLoss) / RSIPeriod)
    return TotalAverageGain, TotalAverageLoss, CurrentChange

#Formula to calculate RSI using average gain and loss
def calcRSI(TotalAverageGain, TotalAverageLoss, CurrentChange, RSIPeriod):
    CurrentGain = 0
    CurrentLoss = 0
    firstRSI = TotalAverageGain / abs(TotalAverageLoss)
    RSI = 100 - (100 / (1 + firstRSI))
    print RSI

    if CurrentChange > 0:
        CurrentGain = CurrentChange
    else:
        CurrentLoss = CurrentChange
    #smoothRSI
    smoothRSI = (((TotalAverageGain * (RSIPeriod - 1)) + CurrentGain) / RSIPeriod) / (((abs(TotalAverageLoss) * (RSIPeriod - 1)) + CurrentLoss) / RSIPeriod)
    finalRSI = 100 - (100 / (1 + smoothRSI))
    return finalRSI

#init block
DaysToDisplay = 1
DaysToStore = DaysToDisplay + 20 #Must always be 20 days greater (for RSI) than DaysToDisplay
CurrentDay = 1
bitcoinHistoricalData = getAPI(DaysToStore)
RSIClosingPrice, BandClosingPrice, RSIValues, LowerBandValues, MiddleBandValues, UpperBandValues = ([] for i in range(6))
RSIPeriod = 14
BandPeriod = 20
print bitcoinHistoricalData['Data']

for i in range(7,22):
    #need to go one above
    RSIClosingPrice.append(bitcoinHistoricalData['Data'][i]['close'])
print RSIClosingPrice
TotalAverageGain, TotalAverageLoss, CurrentChange = calcDailyGains(RSIClosingPrice, RSIPeriod)
finalRSI = calcRSI(TotalAverageGain, TotalAverageLoss, CurrentChange, RSIPeriod)
print finalRSI
