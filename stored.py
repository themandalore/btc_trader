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
	x = x + 1
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
	return x,btce_ETH_buy,btce_ETH_sell,btce_ETH_depth_bid,btce_ETH_depth_ask,krakenETH_bid,krakenETH_ask,k_time,k_bid_vol,k_ask_vol,uc_trans

def preprocess_act(data):
	data_dfc = data
	data_dfc['btce_spread'] = data_dfc['btce_ETH_buy'] - data_dfc['btce_ETH_sell']
	data_dfc['k_spread'] = data_dfc['k_ask'] - data_dfc['K_bid']
	data_dfc['delta_btce_ask'] = data_dfc['btce_ETH_buy'] - data_dfc['btce_ETH_buy'].shift(1)
	data_dfc['delta_btce_bid'] = data_dfc['btce_ETH_sell'] - data_dfc['btce_ETH_sell'].shift(1)
	data_dfc['delta_k_ask'] = data_dfc['k_ask'] - data_dfc['k_ask'].shift(1)
	data_dfc['delta_k_bid'] = data_dfc['K_bid'] - data_dfc['K_bid'].shift(1)
	data_dfc['delta_uc_trans'] = data_dfc['uc_trans'] - data_dfc['uc_trans'].shift(1)
	data_dfc['k_take']=0
	return data_dfc