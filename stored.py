'''Stored Defs'''
import numpy as np
import time, json, requests, csv, datetime
from time import strftime

errors = 0
x= 0

def btceBU(info):
    btceBtcTick = requests.get('https://btc-e.com/api/2/eth_btc/ticker')
    return btceBtcTick.json()['ticker'][info] # replace last with updated etc


def btceDepth(info):
    btceBtcD = requests.get('https://btc-e.com/api/3/depth/eth_btc')
    quantity = 0
    btce_ETH_buy = float(btceBU('buy'))
    btce_ETH_sell = float(btceBU('sell'))
    for i in btceBtcD.json()['eth_btc'][info]:
        if info == 'asks':
            bmark = btce_ETH_sell
        else: bmark = btce_ETH_buy
        if abs(i[0]-bmark) <= 1:
            quantity = quantity + i[1]
        else:
            break

    return quantity




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

def kraken():
    krakenTick = requests.post('https://api.kraken.com/0/public/Depth',data=json.dumps({"pair":"XETHXXBT"}),
    headers={"content-type":"application/json"})
    try: 
        return krakenTick.json()['result']['XETHXXBT']
    except:
        global errors
        errors = errors + 1
        totals = -99999999
        return totals

def toshi_ut():
    toshi_block = requests.get('https://bitcoin.toshi.io/api/v0/transactions/unconfirmed')
    #   totals = toshi_block.json()['inputs']['amount'] + totals
    #for i in toshi_block.json()
    totals = 0 
    try:
        for i in toshi_block.json():
            try:
                totals = totals + i['amount']
                return totals
            except:
                global errors
                errors = errors + 1
                totals = -99999999
                return totals
    except:
        global errors
        errors = errors + 1
        totals = -99999999
        return totals

def get_data():
	global x
	btce_ETH_buy = float(btceBU('buy'))
	btce_ETH_sell = float(btceBU('sell'))
	btce_ETH_depth_bid = float(btceDepth('bids'))
	btce_ETH_depth_ask = float(btceDepth('asks'))
	k_data =  kraken()
	krakenETH_bid= float(k_data['bids'][0][0])
	krakenETH_ask= float(k_data['asks'][0][0])
	k_time = strftime("%Y-%m-%d %H:%M:%S")
	k_bid_vol = float(k_data['bids'][0][1])
	k_ask_vol= float(k_data['asks'][0][1])
	uc_trans = float(toshi_ut())
	okbuy,oksell,okcny = okcoin()
	okbdepth,okadepth = okcoin2()
	return btce_ETH_buy,btce_ETH_sell,btce_ETH_depth_bid,btce_ETH_depth_ask,krakenETH_bid,krakenETH_ask,k_time,k_bid_vol,k_ask_vol,uc_trans,okbuy,oksell,okcny,okadepth,okbdepth

def preprocess_act(data):
	df = data
	df['btce_spread'] = df['btce_ETH_buy'] - df['btce_ETH_sell']
	df['k_spread'] = df['k_ask'] - df['K_bid']
	df['delta_btce_ask'] = df['btce_ETH_buy'] - df['btce_ETH_buy'].shift(1)
	df['delta_btce_bid'] = df['btce_ETH_sell'] - df['btce_ETH_sell'].shift(1)
	df['delta_k_ask'] = df['k_ask'] - df['k_ask'].shift(1)
	df['delta_k_bid'] = df['K_bid'] - df['K_bid'].shift(1)
	df['delta_uc_trans'] = df['uc_trans'] - df['uc_trans'].shift(1)
	df['okc_spread'] = df['okbuy']-df['oksell']
	df['delta_okc_bid'] = df['oksell']-df['oksell'].shift(1)
	df['delta_okc_ask'] = df['okbuy'] - df['okbuy'].shift(1)
	df['delta_okcbdepth'] = df['okbdeth'] = df['okbdeth'].shift(1)
	df['delta_okcadepth'] = df['okadepth'] - df['okadepth'].shift(1)
	df['delta_kbvol'] = df['k_bid_vol']-df['k_bid_vol'].shift(1)
	df['delta_kavol'] = df['k_ask_vol']-df['k_ask_vol'].shift(1)
	df['k_take']=0
	return data_dfc