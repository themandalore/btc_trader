'''Machine Learning program to figure out how to trade'''

'''
fees -- kraken (maker - .16% , taker .26%)
		btce (.2% fee)
		coinbase (maker fee - 0%, taker .25%)

'''

#TAKE OUT difs from dif datasets!!!!!

from sklearn import svm,preprocessing
from pandas import *
import pandas as pd
import numpy as np
from numpy import array
import os,glob
from stored import *

version = 'v2'

directory = 'C:\\Code\\btc\\Trader\\Data\\'
'''
Use prices.csv when ready
'''

classified =version+"_total.csv"

#enter ether quantity to trade (I'm thinking 10 lot, but this quantity could be based later on a maximized quanity)

quantity = 10
control = 500 * quantity #this is the btc price to calculate profits in terms of dollars

numby= 0
nlen = 0
os.chdir(directory)
for file in glob.glob(version+"_*.csv"):
    numby = numby +1
    dfname='df_'+str(numby)
    dfname = pd.DataFrame.from_csv(file)
    nlen = nlen + len(dfname.index)
    if numby == 1:
    	dfone = dfname
    	print('Base:',file)
    else:
    	dfone = dfone.append(dfname,ignore_index=True)
    	print (len(dfone.index))
    	print ('Appended:',file)
    	
    
print (len(dfone.index))
data_dfc = dfone.replace("NaN",0).replace("N/A",0)

def preprocess(data):
	data_dfc = data
	data_dfc['btce_spread'] = data_dfc['btce_ETH_buy'] - data_dfc['btce_ETH_sell']
	data_dfc['k_spread'] = data_dfc['k_ask'] - data_dfc['K_bid']
	data_dfc['delta_btce_ask'] = data_dfc['btce_ETH_buy'] - data_dfc['btce_ETH_buy'].shift(1)
	data_dfc['delta_btce_bid'] = data_dfc['btce_ETH_sell'] - data_dfc['btce_ETH_sell'].shift(1)
	data_dfc['delta_k_ask'] = data_dfc['k_ask'] - data_dfc['k_ask'].shift(1)
	data_dfc['delta_k_bid'] = data_dfc['K_bid'] - data_dfc['K_bid'].shift(1)
	data_dfc['delta_uc_trans'] = data_dfc['uc_trans'] - data_dfc['uc_trans'].shift(1)
	data_dfc['k_time_prof'] = control * (data_dfc['K_bid'].shift(-time_lag)-1.0016 * data_dfc['k_ask'] -.0016*data_dfc['K_bid'].shift(-time_lag))
	data_dfc['btce_time_prof'] =control * ( data_dfc['btce_ETH_sell'].shift(-time_lag)-1.002 * data_dfc['btce_ETH_buy']-.002*data_dfc['btce_ETH_sell'].shift(-time_lag))
	data_dfc['k_take'] = data_dfc.apply(lambda x : 0 if  x['k_time_prof'] <= 0 else 1,axis = 1)
	data_dfc['btce_take'] = data_dfc.apply(lambda x : 0 if  x['btce_time_prof'] <= 0 else 1,axis = 1)
	profit_opps = data_dfc['k_take'].sum(axis=0)
	return data_dfc,profit_opps
time_lag = 0
px = 0 
while (px < numby * 20) and (time_lag < 1):
	time_lag= time_lag+1
	data_dfc,px = preprocess(data_dfc)
	


data_dfc = data_dfc.replace("NaN",0).replace("N/A",0)
data_dfc = data_dfc[1:-1]
data_dfc = data_dfc.reset_index()


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
print ('TL=',time_lag,'profit opps=',px)
print ('Input length:',nlen)
print ('Output length:', len(data_dfc.index))
data_dfc.to_csv(directory+'p_'+classified)

