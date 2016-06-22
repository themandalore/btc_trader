import numpy as np
import time, json, requests, csv, datetime
from time import strftime

errors = 0
x= 0

def okcoin():
    okprice = requests.get('https://www.okcoin.com/api/v1/ticker.do?symbol=btc_usd')
    okcny = requests.get('https://www.okcoin.com/api/v1/ticker.do?symbol=btc_cny')
    return okprice.json()['ticker']['buy'],okprice.json()['ticker']['sell'],okcny.json()['ticker']['last']

def okcoin2():
    okdepth = requests.get('https://www.okcoin.com/api/v1/depth.do?symbol=btc_usd')
    qa = 0
    qb = 0
    for i in okdepth.json()['asks']:
        if abs(okdepth.json()['asks'][0][0] - i[0]) <= 1:
            qa = qa + i[1]
        else:
            break
    for i in okdepth.json()['bids']:
        if abs(okdepth.json()['bids'][0][0] - i[0]) <= 1:
            qb = qb + i[1]
        else:
            break
    return qb,qa



okbuy,oksell,okcny = okcoin()
okbdepth,okadepth = okcoin2()
print ('buy',okbuy,'//sell',oksell,'//cny',okcny)
print(okbdepth)
print(okadepth)