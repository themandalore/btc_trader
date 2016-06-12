import transact, pickle
from transact import api
api = api()
import pandas as pd
import numpy as np
from stored import *
from numpy import array
from transact_k import *

'''
Get API stuff from the data pull (use defs)
Get Account balances
Pull in classifier
Keep track of all open orders, positions, and expected/ actual profits
'''


version = 'v2'
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

titles =  ('obs','btce_ETH_buy','btce_ETH_sell','btce_ETH_depth_bid','btce_ETH_depth_ask','K_bid','k_ask','k_time','k_bid_vol','k_ask_vol','uc_trans')
print (titles)
x=0
time_lag = 4
pname = version + '_classifier.pickle'
pickle_in = open('Classifiers/'+ pname,'rb')
clf = pickle.load(pickle_in)

name='activetrader.csv'
with open(name, 'w') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(titles)

def newrow():
	global x
	with open(r'activetrader.csv', 'a') as f:
		x,btce_ETH_buy,btce_ETH_sell,btce_ETH_depth_bid,btce_ETH_depth_ask,krakenETH_bid,krakenETH_ask,k_time,k_bid_vol,k_ask_vol,uc_trans = get_data()
		outstring = int(x),float(btce_ETH_buy),float(btce_ETH_sell),float(btce_ETH_depth_bid),float(btce_ETH_depth_ask),float(krakenETH_bid),float(krakenETH_ask),k_time,float(k_bid_vol),float(k_ask_vol),float(uc_trans)
		k_bid = float(krakenETH_bid)
		k_ask = float(krakenETH_ask)
		writer = csv.writer(f)
		writer.writerow(outstring)
		x = x + 1
		return k_bid, k_ask
		print (outstring)
#This pulls in our classifier

while x < 4:
	k_bid,k_ask = newrow()

while x < 6:
	newrow()
	df = pd.DataFrame.from_csv('activetrader.csv')
	df = df.replace("NaN",0).replace("N/A",0)
	preprocess_act(df)
	df = df [1:]
	df2 = df[:1]


	XX = (array(df2[features].values).tolist())
	a = clf.predict(XX)
	print (a)
	if a[:1] == 0:
		'''
		Now buy on Kraken, and sell in 3 cycles
		'''
		'''get current best ask price and place limit'''
		print(k_balance())
		'''
		print (k_trade_eth('buy','1','bbuy')
		time.sleep(15) # 120 equals two minutes
		print (k_trade_eth('sell','1','bsell'))'''
	elif a[:1]==1:
		print (k_trade_eth('buy','10',k_ask)
			time.sleep((time_lag-1)*5)
			k_data =  kraken()
			new_bids= float(k_data['bids'][0][0])
		print (k_trade_eth('sell','10',new_bids)
	else:
		print ('ERROR')

'''
BTCE
'''

#This gets the BTCE open orders
print(api.ActiveOrders(tpair='eth_btc'))


#This is how you trade
'''
print (api.Trade(tpair='eth_btc',ttype='buy',trate=.026,tamount=1))

'''


#This is how you cancel an order
#print (api.CancelOrder(torder_id=1084020979))

print(api.ActiveOrders(tpair='eth_btc'))

'''
Kraken 
'''

print(k_open())

print ('Errors:',errors)