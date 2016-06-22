import transact, pickle,time
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
time_lag = 10
pname = version + '_classifier.pickle'
pickle_in = open('Classifiers/'+ pname,'rb')
clf = pickle.load(pickle_in)

name='activetrader.csv'
with open(name, 'w') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(titles)

print('Starting Balance:',k_balance())
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
		print (outstring)
		return k_bid, k_ask
		
#This pulls in our classifier

while x < 4:
	k_bid,k_ask = newrow()
	time.sleep(5)

trades = 0 
while trades < 1:
	newrow()
	df = pd.DataFrame.from_csv('activetrader.csv')
	df = df.replace("NaN",0).replace("N/A",0)
	preprocess_act(df)
	df = df [1:]
	df2 = df.tail(1)


	XX = (array(df2[features].values).tolist())
	a = clf.predict(XX)
	print (XX)
	if a[:1] == 0:
		'''
		Now buy on Kraken, and sell in 3 cycles
		'''
		'''get current best ask price and place limit'''
		time.sleep(4)
		print ('None:', x - 4)
		

	elif a[:1]==1:
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

print('Open Orders:',k_open())

print ('Errors:',errors)

print('Ending Balance Balance:',k_balance())

'''
Test ones
[  4.00000000e-05   1.20000000e-04   0.00000000e+00   1.00000000e-05   0.00000000e+00  -7.60000000e-05   0.00000000e+00]
[[5.000000000000143e-05, 0.00028800000000000006, -9.999999999999593e-06, 0.0, 0.0, 0.0, 0.0]]

What we use:


'''