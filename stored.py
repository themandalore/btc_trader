'''Stored Defs'''
import numpy as np
import time, json, requests, csv, datetime
from time import strftime
import pandas as pd
import sys
sys.path.insert(0, 'C:/Code/PY_libs/GDAX')
import PublicClient

features = ["btce_spread",
			"k_spread",
			'k_btce_diff',
			"delta_btce_ask",
			"delta_btce_bid",
			"delta_k_ask",
			"delta_k_bid",
			"delta_uc_trans",
			"okc_spread",
			"delta_okc_bid",
			"delta_okc_ask",
			"k_gradient_diff",
			#"delta_okcbdepth",
			#"delta_okcadepth",
			"delta_kbvol",
			"delta_kavol",
			"ma_diff5",
			"ma_diff20",
			#'ok_btce_diff',
			#'ok_k_diff',
			'k_imbalance',
			'cb_adj_imb',
			'cb_spread',
			'cbma_diff5',
			'cbma_diff20',
			'okc_cb_diff',
			'delta_cb_spread',
			'cb_k_diff',
			'cb_btce_diff',
			'cb_vol5',
			'cb_vol20',
			'delta_cb_USD',
			]

            
k_good_feats = ['k_spread', 'k_imbalance', 'btce_spread', 'delta_okc_ask', 'delta_kavol', 'cbma_diff20', 'delta_cb_spread', 'ma_diff20', 'ma_diff5', 'delta_kbvol', 'k_gradient_diff', 'okc_cb_diff', 'delta_okc_bid', 'delta_uc_trans', 'cb_k_diff', 'delta_k_ask', 'okc_spread', 'delta_btce_bid']
cb_good_feats = ['k_imbalance', 'k_spread', 'btce_spread', 'delta_okc_ask', 'delta_kavol', 'delta_kbvol', 'cbma_diff20', 'delta_cb_spread', 'ma_diff20', 'k_gradient_diff', 'ma_diff5', 'delta_btce_bid', 'okc_cb_diff', 'delta_okc_bid', 'okc_spread']

errors = 0
def gdax(base_prod):
	USD = PublicClient.getProductTicker(product="BTC-USD")['price']
	ticker = PublicClient.getProductTicker(product=base_prod)
	bid=ticker['bid']
	ask = ticker['ask']
	Book = PublicClient.getProductOrderBook(level=2, product=base_prod)
	b_depth=0
	a_depth=0
	a_grade=0
	b_grade=0
	for i in Book['asks']:
		a_depth = a_depth + float(i[1])
		a_grade= a_grade + float(i[0])*float(i[1])
	for i in Book['bids']:
		b_depth= b_depth + float(i[1])
		b_grade= b_grade + float(i[0])*float(i[1])
	adj_imb = a_grade/b_grade
	return USD, bid, ask,b_depth,a_depth,adj_imb

def USD_gdax():
	USD = PublicClient.getProductTicker(product="BTC-USD")['price']
	return USD

def mmgdax(base_prod):
	ticker = PublicClient.getProductTicker(product=base_prod)
	bid=ticker['bid']
	ask = ticker['ask']
	return bid, ask

'''
Get bid/ask , depth (imbalance/ gradients), USD price (for OKC comp)
Then build trading mechanisms
'''


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
	try:
		okprice = requests.get('https://www.okcoin.com/api/v1/ticker.do?symbol=btc_usd',timeout=(3, 10))
		okcny = requests.get('https://www.okcoin.com/api/v1/ticker.do?symbol=btc_cny',timeout=(3, 10))
		return okprice.json()['ticker']['buy'],okprice.json()['ticker']['sell'],okcny.json()['ticker']['last']
	except:
		global errors
		errors = errors + 1
		return -999999,-99999
def okcoin2():
	try:
		okdepth = requests.get('https://www.okcoin.com/api/v1/depth.do?symbol=btc_usd',timeout=(1, 1))
		a = 0
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
	except: 
		global errors
		errors = errors + 1
		return -999999,-99999

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
	global errors
	USD, bid, ask,b_depth,a_depth,adj_imb = gdax('ETH-BTC')
	cb_USD = float(USD)
	cb_bid = float(bid)
	cb_ask = float (ask)
	cb_bdepth=float(b_depth)
	cb_adepth = float(a_depth)
	cb_adj_imb = float(adj_imb)
	btce_ETH_buy = float(btceBU('buy'))
	btce_ETH_sell = float(btceBU('sell'))
	btce_ETH_depth_bid = float(btceDepth('bids'))
	btce_ETH_depth_ask = float(btceDepth('asks'))
	k_data =  kraken()
	try:
		krakenETH_bid= float(k_data['bids'][0][0])
	except:
		errors = errors + 1
		krakenETH_bid = -99999999
	try:
		krakenETH_ask= float(k_data['asks'][0][0])
	except:
		errors = errors + 1
		krakenETH_ask = -99999999
	try:
		k_time = strftime("%Y-%m-%d %H:%M:%S")
	except:
		errors = errors + 1
		k_time = -99999999
	try:
		levels = 0 
		k_bid_vol = 0
		k_ask_vol = 0
		k_b = 0
		k_a = 0
		while levels < 6:
			k_bid_vol = float(k_data['bids'][levels][1]) + k_bid_vol
			k_ask_vol= float(k_data['asks'][levels][1])+k_bid_vol
			levels = levels + 1


		total_bdepth = 0
		for lev in k_data['bids']:
			if  abs(krakenETH_bid - float(k_data['bids'][levels][0])) < .01:
				total_bdepth += float(k_data['bids'][levels][1])
				max_b = float(k_data['bids'][levels][0])
			else:
				break
		total_adepth = 0
		for lev in k_data['asks']:
			if  abs(krakenETH_bid - float(k_data['asks'][levels][0])) < .01:
				total_adepth += float(k_data['asks'][levels][1])
				max_a = float(k_data['asks'][levels][0])
			else:
				break
		k_b_gradient =  (abs(total_bdepth - k_bid_vol))/(abs(max_b - (krakenETH_bid +float(k_data['bids'][5][0]))/2))
		k_a_gradient =  (abs(total_adepth - k_ask_vol))/(abs(max_a - (krakenETH_ask +float(k_data['asks'][5][0]))/2))
	except:
		errors = errors + 1
		k_bid_vol = -99999999
		k_ask_vol = -99999999
		k_b_gradient = -999999
		k_a_gradient = -9999999
	uc_trans = float(toshi_ut())
	try:
		okbuy,oksell,okcny = okcoin()
	except:
		errors = errors + 1
		okbuy,oksell,okcny = -99999999,-99999999,-99999999
	okbdepth,okadepth = okcoin2()
	return btce_ETH_buy,btce_ETH_sell,btce_ETH_depth_bid,btce_ETH_depth_ask,krakenETH_bid,krakenETH_ask,k_time,k_bid_vol,k_ask_vol,k_a_gradient,k_b_gradient,uc_trans,okbuy,oksell,okcny,okadepth,okbdepth,cb_USD,cb_bid,cb_ask,cb_bdepth,cb_adepth,cb_adj_imb

def preprocess_act(data):
	df = data
	#print (df.head())
	df['btce_spread'] = df['btce_ETH_buy'] - df['btce_ETH_sell']
	df['k_spread'] = df['k_ask'] - df['K_bid']
	df['k_btce_diff'] = df['btce_ETH_sell'] - df['K_bid']
	df['ok_k_diff']=df['K_bid']-df['oksell']
	df['ok_btce_diff']=df['btce_ETH_sell']-df['oksell']
	df['delta_btce_ask'] = df['btce_ETH_buy'] - df['btce_ETH_buy'].shift(1)
	df['delta_btce_bid'] = df['btce_ETH_sell'] - df['btce_ETH_sell'].shift(1)
	df['delta_k_ask'] = df['k_ask'] - df['k_ask'].shift(1)
	df['delta_k_bid'] = df['K_bid'] - df['K_bid'].shift(1)
	df['delta_uc_trans'] = df['uc_trans'] - df['uc_trans'].shift(1)
	df['okc_spread'] = df['okbuy']-df['oksell']
	df['delta_okc_bid'] = df['oksell']-df['oksell'].shift(1)
	df['delta_okc_ask'] = df['okbuy'] - df['okbuy'].shift(1)
	df['delta_okcbdepth'] = df['okbdepth'] = df['okbdepth'].shift(1)
	df['delta_okcadepth'] = df['okadepth'] - df['okadepth'].shift(1)
	df['delta_kbvol'] = df['k_bid_vol']-df['k_bid_vol'].shift(1)
	df['delta_kavol'] = df['k_ask_vol']-df['k_ask_vol'].shift(1)
	df['k_imbalance']=df['k_ask_vol']-df['k_bid_vol']
	df['k_gradient_diff']=df['k_a_gradient']/df['k_b_gradient']
	df['kprice_ma'] = pd.rolling_mean(df['k_ask'],5)
	df['ma_diff5'] = df['kprice_ma']-df['k_ask']
	df['kprice_ma2'] = pd.rolling_mean(df['k_ask'],20)
	df['ma_diff20'] = df['kprice_ma']-df['k_ask']
	df['k_take']=0
	df['cb_take']=0
	df['cb_spread']=df['cb_ask']-df['cb_bid']
	df['okc_cb_diff']=df['cb_USD']-df['oksell']
	df['delta_cb_USD']=df['cb_USD'] - df['cb_USD'].shift(1)
	df['cbprice_ma'] = pd.rolling_mean(df['cb_ask'],5)
	df['cbma_diff5'] = df['cbprice_ma']-df['cb_ask']
	df['cbprice_ma2'] = pd.rolling_mean(df['cb_ask'],20)
	df['cbma_diff20'] = df['cbprice_ma']-df['cb_ask']
	df['delta_cb_spread']=df['cb_spread'] - df['cb_spread'].shift(1)
	df['cb_k_diff']=df['cb_ask']-df['k_ask']
	df['cb_btce_diff']=df['cb_ask']-df['btce_ETH_sell']
	df['cb_vol5']=pd.rolling_std(df['cb_ask'],5)
	df['cb_vol20']=pd.rolling_std(df['cb_ask'],20)
	return df

quantity = 10
control = 500 * quantity 

def preprocess(data):
	df = preprocess_act(data)
	df['k_time_prof'] = control * (df['delta_k_bid'].shift(-1) - .0016 * df['k_ask'] -.0016*df['K_bid'].shift(-1))
	df['btce_time_prof'] =control * ( df['btce_ETH_sell'].shift(-1)-1.002 * df['btce_ETH_buy']-.002*df['btce_ETH_sell'].shift(-1))
	df['k_take'] = df.apply(lambda x : 1 if  x['k_time_prof'] > 0 else 0,axis = 1)
	df['btce_take'] = df.apply(lambda x : 1 if  x['btce_time_prof'] > 0 else 0,axis = 1)
	kprofit_opps = df['k_take'].sum(axis=0)
	df['cb_time_prof']=control * (df['cb_bid'].shift(-1)- df['cb_ask'])
	df['cb_take']=df.apply(lambda x : 1 if  x['cb_time_prof'] > 0 else 0,axis = 1)
	cbprofit_opps=df['cb_take'].sum(axis=0)
	return df,kprofit_opps,cbprofit_opps