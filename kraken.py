
import time, json, requests, csv

def coinbase():
    coinBaseTick = requests.post('https://api.coinbase.com/v2/products/BTC-USD/ticker',headers={"content-type":"application/json","CB-VERISON":"2016-02-2014"})
    print (coinBaseTick.json()) # replace amount with currency etc
coinbase()