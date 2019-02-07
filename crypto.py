import requests
import json
from pprint import pprint

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

#Formula to calculate RSI
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
