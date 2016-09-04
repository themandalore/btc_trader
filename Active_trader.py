import transact, pickle,time
from transact import api
api = api()
import pandas as pd
import numpy as np
from stored import *
from numpy import array
from transact_k import *
from transact_cb import *
import shutil, os


'''
Get API stuff from the data pull (use defs)
Get Account balances
Pull in classifier
Keep track of all open orders, positions, and expected/ actual profits
'''

TRADE = False
PREDICT = False
breaker = 0
exchange = 'kraken'
if exchange == 'kraken':
	good_feats = k_good_feats
elif exchange == 'coinbase':
	good_feats = cb_good_feats

while True:
	date = strftime("%Y-%m-%d")
	version = 'v5'
	imp = version + '_data'
	import imp
	#This gets API data

	titles =  ('obs','btce_ETH_buy','btce_ETH_sell','btce_ETH_depth_bid','btce_ETH_depth_ask','K_bid','k_ask','k_time','k_bid_vol','k_ask_vol','k_a_gradient','k_b_gradient','uc_trans','okbuy','oksell','okcny','okadepth','okbdepth','cb_USD','cb_bid','cb_ask','cb_bdepth','cb_adepth','cb_adj_imb')
	print (titles)
	x=0
	#55 works out to about a minute
	time_lag = 54 
	if PREDICT:
		pname = version + '_'+exchange+'_classifier.pickle'
		pickle_in = open('Classifiers/'+ pname,'rb')
		clf = pickle.load(pickle_in)

	name = 'Data/' + version + '_' + date + '.csv'
	with open(name, 'w') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
		spamwriter.writerow(titles)
	try:
		print('Kraken Starting Balance:',k_balance())
		print('Coinbase Starting Balance:')
		print('BTCE Starting Balance:')
	except:
		print('Starting Balance: Error')
	def newrow():
		global x
		with open(r'Data/' + version + '_' + date + '.csv', 'a') as f:
			x=x+1
			btce_ETH_buy,btce_ETH_sell,btce_ETH_depth_bid,btce_ETH_depth_ask,krakenETH_bid,krakenETH_ask,k_time,k_bid_vol,k_ask_vol,k_a_gradient,k_b_gradient,uc_trans,okbuy,oksell,okcny,okadepth,okbdepth,cb_USD,cb_bid,cb_ask,cb_bdepth,cb_adepth,cb_adj_imb = get_data()
			outstring = int(x),float(btce_ETH_buy),float(btce_ETH_sell),float(btce_ETH_depth_bid),float(btce_ETH_depth_ask),float(krakenETH_bid),float(krakenETH_ask),k_time,float(k_bid_vol),float(k_ask_vol),float(k_a_gradient),float(k_b_gradient),float(uc_trans),float(okbuy),float(oksell),float(okcny),float(okadepth),float(okbdepth),float(cb_USD),float(cb_bid),float(cb_ask),float(cb_bdepth),float(cb_adepth),float(cb_adj_imb)
			k_bid = float(krakenETH_bid)
			k_ask = float(krakenETH_ask)
			writer = csv.writer(f)
			writer.writerow(outstring)
			print (outstring)
			return k_bid, k_ask
			
	while x < 20:
		try:
			k_bid,k_ask = newrow()
			time.sleep(time_lag)
		except:
			print ('DATA ERROR')
			errors += 1
	trades = 0 
	while x > 19 :
		try:
			newrow()
		except:
			break
		if PREDICT:
			df = pd.DataFrame.from_csv(name)
			df = df.replace("NaN",-99999).replace("N/A",-99999)
			#df = df.dropna(inplace=True)
			preprocess_act(df)
			df = df [1:]
			df2 = df.tail(1)
			XX = (array(df2[good_feats].values).tolist())
			a = clf.predict(XX)
			print (XX)
			if a[:1] == 0:
				print ('None:', x - 4)
				time.sleep(time_lag-1)
				if date != strftime("%Y-%m-%d"):
					break
			elif a[:1]==1 and TRADE:
				trades =+ 1
				min_sp = k_ask - k_bid
				new_bids = min_sp + .0002
				print (k_trade_eth('buy','10',min_sp))
				print (k_trade_eth('sell','10',new_bids))
				exp_prof = (new_bids-min_sp) * 10
				print ('Exp Profit:',exp_prof)
				print(k_balance())
				time.sleep(time_lag-5)
				if exp_prof < 0:
					breaker = 1
					break
				else:
					pass
			elif a[:1]==1:
				print (k_ask)
				time.sleep(time_lag-1)
				k_data =  kraken()
				new_bids= float(k_data['bids'][0][0])
				print ('Exp Profit:',(new_bids-k_ask) * 10)
				breaker = 1
				break
			else:
				print ('ERROR')
				time.sleep(time_lag-1)
		else: 
			time.sleep(time_lag)
			if date != strftime("%Y-%m-%d"):
				break
	try:
		print('Open Orders:',k_open())
		print('Ending Balance Balance:',k_balance())
	except:
		pass
	print ('Errors:',errors)
	if breaker > 0:
		break
