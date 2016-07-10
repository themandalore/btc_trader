import transact, pickle,time
from transact import api
api = api()
import pandas as pd
import numpy as np
from stored import *
from numpy import array
from transact_k import *
import shutil, os


'''
Get API stuff from the data pull (use defs)
Get Account balances
Pull in classifier
Keep track of all open orders, positions, and expected/ actual profits
'''

TRADE = False
PREDICT = False

while True:
	date = strftime("%Y-%m-%d")
	version = 'v3'
	imp = version + '_data'
	import imp
	#This gets API data
	features = ["btce_spread",
				"k_spread",
				"delta_btce_ask",
				"delta_btce_bid",
				"delta_k_ask",
				"delta_k_bid",
				"delta_uc_trans"
	           ]


	titles =  ('obs','btce_ETH_buy','btce_ETH_sell','btce_ETH_depth_bid','btce_ETH_depth_ask','K_bid','k_ask','k_time','k_bid_vol','k_ask_vol','uc_trans','okbuy','oksell','okcny','okadepth','okbdepth')
	print (titles)
	x=0
	#55 works out to about a minute
	time_lag = 55 
	if PREDICT:
		pname = version + '_classifier.pickle'
		pickle_in = open('Classifiers/'+ pname,'rb')
		clf = pickle.load(pickle_in)

	name = 'Data/' + version + '_' + date + '.csv'
	with open(name, 'w') as csvfile:
	    spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	    spamwriter.writerow(titles)

	print('Starting Balance:',k_balance())
	def newrow():
		global x
		with open(r'Data/' + version + '_' + date + '.csv', 'a') as f:
			x=x+1
			btce_ETH_buy,btce_ETH_sell,btce_ETH_depth_bid,btce_ETH_depth_ask,krakenETH_bid,krakenETH_ask,k_time,k_bid_vol,k_ask_vol,uc_trans,okbuy,oksell,okcny,okadepth,okbdepth = get_data()
			outstring = int(x),float(btce_ETH_buy),float(btce_ETH_sell),float(btce_ETH_depth_bid),float(btce_ETH_depth_ask),float(krakenETH_bid),float(krakenETH_ask),k_time,float(k_bid_vol),float(k_ask_vol),float(uc_trans),float(okbuy),float(oksell),float(okcny),float(okadepth),float(okbdepth)
			k_bid = float(krakenETH_bid)
			k_ask = float(krakenETH_ask)
			writer = csv.writer(f)
			writer.writerow(outstring)
			print (outstring)
			return k_bid, k_ask
			
	#This pulls in our classifier

	while x < 4:
		k_bid,k_ask = newrow()
		time.sleep(time_lag)

	trades = 0 
	while trades < 1:
		newrow()
		if PREDICT:
			df = pd.DataFrame.from_csv(name)
			df = df.replace("NaN",0).replace("N/A",0)
			preprocess_act(df)
			df = df [1:]
			df2 = df.tail(1)
			XX = (array(df2[features].values).tolist())
			a = clf.predict(XX)
			print (XX)
			if a[:1] == 0:
				print ('None:', x - 4)
				time.sleep(time_lag)
				if date != strftime("%Y-%m-%d"):
					break
			
			
			elif a[:1]==1 and TRADE:
				trades =+ 1
				print (k_trade_eth('buy','10',k_ask))
				time.sleep((time_lag-1)*5)
				k_data =  kraken()
				new_bids= float(k_data['bids'][0][0])
				print (k_trade_eth('sell','10',new_bids))
				print ('Exp Profit:',(new_bids-k_ask) * 10)
				print(k_balance())
			else:
				print ('ERROR')
				time.sleep(time_lag)
		else: 
			time.sleep(time_lag)
			if date != strftime("%Y-%m-%d"):
				break
	print('Open Orders:',k_open())
	print('Ending Balance Balance:',k_balance())
	print ('Errors:',errors)
