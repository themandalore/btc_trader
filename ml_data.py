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

test_size = 500

features = ["btce_spread",
			"k_spread",
			"delta_btce_ask",
			"delta_btce_bid",
			"delta_k_ask",
			"delta_k_bid",
			"delta_uc_trans"
           ]
            
directory = 'C:\\Code\\btc\\Trader\\'
'''
Use prices.csv when ready
'''
classified = 'ml_learned.csv'

#to_predict =  ['k_take', 'k_take2','k_take3','btce_take','btce_take2','btce_take3']
to_predict = 'k_take3'

data_df = pd.DataFrame.from_csv(directory + classified)
data_df = data_df.reset_index()
data_df = data_df.reindex(np.random.permutation(data_df.index))
data_dfc = data_df.replace("NaN",0).replace("N/A",0)
data_dfm = data_dfc[-test_size:]
data_dfc = data_dfc[:test_size]
newIndexList=range(0,len(data_dfm))
data_dfm['ni']= newIndexList
data_dfm=data_dfm.set_index('ni')
#print (data_df.describe())

X = (array(data_dfc[features].values).tolist())
X = preprocessing.scale(X)
print (X.std(),X.mean())

y = (data_dfc[to_predict]
         .values.tolist())
XX = (array(data_dfm[features].values).tolist())
XX = preprocessing.scale(XX)
YY = (data_dfm[to_predict]
         .values.tolist())

lin_svc = svm.LinearSVC(C=1).fit(X,y)
a = lin_svc.predict(XX)
ndarr = np.asarray(a) # if ndarr is actually an array, skip this
fast_df = pd.DataFrame({"new_type": ndarr.ravel()})
a.tolist()
data_dfm['new_type'] =  fast_df['new_type']
data_dfm.to_csv('final_learned.csv')
