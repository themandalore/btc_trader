'''Machine Learning program to figure out how to trade'''
'''
To do
Pull in dataset
Figure out how to detect arb opportunites and trade them

'''


'''
Get:
fees -- kraken (maker - .16% , taker .26%)
		btce (.2% fee)
		coinbase (maker fee - 0%, taker .25%)

'''


from sklearn import svm,preprocessing
from pandas import *
import pandas as pd
import numpy as np
from numpy import array

test_size = 2000
         
directory = 'C:\\Code\\btc\\Trader\\'
'''
Use prices.csv when ready
'''
classified = 'prices.csv'

#enter ether quantity to trade (I'm thinking 10 lot, but this quantity could be based later on a maximized quanity)
quantity = 10
control = 450 * quantity #this is the btc price to calculate profits in terms of dollars


data_df = pd.DataFrame.from_csv(directory + classified)
data_df = data_df.reset_index()
data_dfc = data_df.replace("NaN",0).replace("N/A",0)
data_dfc = data_dfc[:test_size]

data_dfc['btce_spread'] = data_dfc['btce_ETH_buy'] - data_dfc['btce_ETH_sell']
data_dfc['k_spread'] = data_dfc['k_ask'] - data_dfc['K_bid']
data_dfc['delta_btce_ask'] = data_dfc['btce_ETH_buy'] - data_dfc['btce_ETH_buy'].shift(1)
data_dfc['delta_btce_bid'] = data_dfc['btce_ETH_sell'] - data_dfc['btce_ETH_sell'].shift(1)
data_dfc['delta_k_ask'] = data_dfc['k_ask'] - data_dfc['k_ask'].shift(1)
data_dfc['delta_k_bid'] = data_dfc['K_bid'] - data_dfc['K_bid'].shift(1)
data_dfc['delta_uc_trans'] = data_dfc['uc_trans'] - data_dfc['uc_trans'].shift(1)
data_dfc['k_time_prof'] = control * (data_dfc['K_bid'].shift(-1)-1.0016 * data_dfc['k_ask'] -.0016*data_dfc['K_bid'].shift(-1))
data_dfc['btce_time_prof'] =control * ( data_dfc['btce_ETH_sell'].shift(-1)-1.002 * data_dfc['btce_ETH_buy']-.002*data_dfc['btce_ETH_sell'].shift(-1))
data_dfc['k_time_prof2'] = control * (data_dfc['K_bid'].shift(-2)-1.0016 * data_dfc['k_ask'] -.0016*data_dfc['K_bid'].shift(-2))
data_dfc['btce_time_prof2'] =control * ( data_dfc['btce_ETH_sell'].shift(-2)-1.002 * data_dfc['btce_ETH_buy']-.002*data_dfc['btce_ETH_sell'].shift(-2))
data_dfc['k_time_prof3'] = control * (data_dfc['K_bid'].shift(-3)-1.0016 * data_dfc['k_ask'] -.0016*data_dfc['K_bid'].shift(-3))
data_dfc['btce_time_prof3'] =control * ( data_dfc['btce_ETH_sell'].shift(-3)-1.002 * data_dfc['btce_ETH_buy']-.002*data_dfc['btce_ETH_sell'].shift(-3))



data_dfc = data_dfc.replace("NaN",0).replace("N/A",0)
data_dfc = data_dfc[1:-1]
data_dfc = data_dfc.reset_index()

data_dfc['k_take'] = data_dfc.apply(lambda x : 0 if  x['k_time_prof'] <= 0 else 1,axis = 1)
data_dfc['btce_take'] = data_dfc.apply(lambda x : 0 if  x['btce_time_prof'] <= 0 else 1,axis = 1)
data_dfc['k_take2'] = data_dfc.apply(lambda x : 0 if  x['k_time_prof2'] <= 0 else 1,axis = 1)
data_dfc['btce_take2'] = data_dfc.apply(lambda x : 0 if  x['btce_time_prof2'] <= 0 else 1,axis = 1)
data_dfc['k_take3'] = data_dfc.apply(lambda x : 0 if  x['k_time_prof3'] <= 0 else 1,axis = 1)
data_dfc['btce_take3'] = data_dfc.apply(lambda x : 0 if  x['btce_time_prof3'] <= 0 else 1,axis = 1)




'''
Buy lowest, sell highest exchange

data_dfc['buy_ex'] = data_dfc.apply(lambda x : 'btce' if  x['k_ask'] > x['btce_ETH_buy'] else 'k',axis = 1)
data_dfc['lowest_buy'] = data_dfc.apply(lambda x : x['btce_ETH_buy'] if  x['k_ask'] > x['btce_ETH_buy'] else x['k_ask'],axis = 1)
data_dfc['bfee'] = data_dfc.apply(lambda x : .002 if  x['k_ask'] > x['btce_ETH_buy'] else .0016 ,axis = 1)

data_dfc['sell_ex'] = data_dfc.apply(lambda x : 'btce' if x['K_bid'] < x['btce_ETH_sell'] else 'k',axis = 1)
data_dfc['highest_sell'] = data_dfc.apply(lambda x : x['btce_ETH_sell'] if x['K_bid'] < x['btce_ETH_sell']  else x['K_bid'],axis = 1)
data_dfc['sfee'] = data_dfc.apply(lambda x : .002 if  x['K_bid'] < x['btce_ETH_sell'] else .0016 ,axis = 1)

data_dfc['cx_profit'] = quantity * data_dfc['highest_sell'] - data_dfc['highest_sell'] * data_dfc['sfee'] - data_dfc['lowest_buy']*data_dfc['bfee'] - data_dfc['lowest_buy']* quantity

data_dfc['action'] = data_dfc.apply(lambda x : 'None' if  x['cx_profit'] <= 0 else str('Buy at'+ data_dfc['buy_ex'] + 'and Sell at:' + data_dfc['sell_ex']) ,axis = 1)
'''

'''
Capture Spread on exchange
'''
data_dfc['sp_k_profit'] = data_dfc['k_spread'] * quantity - (.0032 * quantity * data_dfc['k_spread'] )
data_dfc['sp_btce_profit'] = data_dfc['btce_spread'] * quantity - (.0032 * quantity * data_dfc['btce_spread'] )


print (data_dfc.head())
data_dfc.to_csv('ml_learned.csv')

