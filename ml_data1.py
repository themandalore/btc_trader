'''Machine Learning program to figure out how to trade'''
'''
To do
Set up live Trader

Get historical data (days in files)
Get summary stats of trades 
	-time of day to trade
Get Poloniex data
Get coinbase data

Optimize time to hold
Optimize volume to trade

Do multiple way trades

Continue to test new algorithims if accuracy goes below 99%
Add new features if accuracy goes below 99%
Add new exchange eventually

Get:
fees -- kraken (maker - .16% , taker .26%)
		btce (.2% fee)
		coinbase (maker fee - 0%, taker .25%)

'''


from sklearn import preprocessing, cross_validation, svm
from pandas import *
import pandas as pd
import numpy as np
import math
from numpy import array
import pickle

version = 'v2'

features = ["btce_spread",
			"k_spread",
			"delta_btce_ask",
			"delta_btce_bid",
			"delta_k_ask",
			"delta_k_bid",
			"delta_uc_trans"
           ]
            
directory = 'C:\\Code\\btc\\Trader\\Data\\'
'''
Use prices.csv when ready
'''


directory = 'C:\\Code\\btc\\Trader\\Data\\'
'''
Use prices.csv when ready
'''
classified = 'p_'+version + '_total.csv'

#to_predict =  ['k_take', 'k_take2','k_take3','btce_take','btce_take2','btce_take3']
to_predict = 'k_take'
prof_pred = 'k_time_prof'
cols = np.array(features)
cols = np.append(cols,to_predict)
data_dfi = pd.DataFrame.from_csv(directory + classified)
data_df=data_dfi[cols]
print (data_df.head())
data_df = data_df.reset_index()
dfc = data_df.reindex(np.random.permutation(data_df.index))
dfc.fillna(value=-99999, inplace=True)
forecast_out = int(math.ceil(0.01 * len(dfc)))
dfx = dfc[features]
X = np.array(dfx)
dfc.dropna(inplace=True)
y = np.array(dfc[to_predict])


X_train, X_test, y_train, y_test = cross_validation.train_test_split(X,y,test_size = .3)


#print (data_df.describe())
print (X[0])
clf = svm.LinearSVC(C=1).fit(X,y)
clf.fit(X_train, y_train)
pname = 'Classifiers/'+version + '_classifier.pickle'
with open(pname,'wb') as f:
	pickle.dump(clf,f)


accuracy = clf.score(X_test,y_test)
print ('Accuracy', accuracy)
print ('Length of Dataset',len(dfc))
print ('Time in Dataset',len(dfc)/12/60,'hours')
print ('Number of Opportunities',data_df[data_df[to_predict]>0].count()[to_predict])
print ('Expected Profit: ', accuracy * (data_dfi[data_dfi[prof_pred]>0].sum()[prof_pred]))

#this treats each row as a day and pushes it back for graphing purposes
'''
lin_svc = svm.LinearSVC(C=1).fit(X,y)
a = lin_svc.predict(XX)
ndarr = np.asarray(a) # if ndarr is actually an array, skip this
fast_df = pd.DataFrame({"new_type": ndarr.ravel()})
a.tolist()
data_dfm['new_type'] =  fast_df['new_type']
data_dfm.to_csv('final_learned.csv')
'''