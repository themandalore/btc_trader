'''Machine Learning--strategies'''
'''
Test bollinger bands (optimize band width)
	- optimize hold Time
	-band to buy, band to sell 


'''


from sklearn import preprocessing, cross_validation, svm
from sklearn.cross_validation import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from pandas import *
import pandas as pd
import numpy as np
from numpy import array
import pickle, math, warnings
from operator import itemgetter, attrgetter, methodcaller
warnings.filterwarnings("ignore", category=DeprecationWarning) 

directory = 'C:\\Code\\btc\\Trader\\Data\\'
'''
Use prices.csv when ready
'''


directory ='C:\\Code\\btc\\Trader\\Data\\'
classified = '_ready_gdax_60_fmt' +'.csv'
df = pd.DataFrame.from_csv(directory + classified)
df['time'] = pd.to_datetime(df['time'])
df = df.sort(['time'])

# df['price'] = (df.low + df.high)/2
# df['prof'] = df.price.shift(-30)-df.price -df.price*.005
# df['take'] = df.apply(lambda x : 1 if  x['prof'] > 0 else 0,axis = 1)
# df['pdelta'] = df.price - df.price.shift(1)
# df['ma'] = pd.rolling_mean(df.price,5)
# df['ma_diff'] = df.price -df['ma']
# df['volatility']=pd.rolling_std(df['pdelta'],20)**2
# df['uband']=df['ma'] + pd.rolling_std(df.price,20)
# df['bband']=df['ma'] - pd.rolling_std(df.price,20)
# df['u_take']=df.apply(lambda x : 1 if  x['uband'] < x['price'] else 0,axis = 1)
# df['b_take']=df.apply(lambda x : 1 if  x['bband'] > x['price'] else 0,axis = 1)
# df.to_csv(directory + '_ready_'+classified)
df = df.tail(20000)
to_predict = 'take'
features = ['volatility','ma_diff','pdelta','u_take','b_take']
cols = np.array(features)
cols = np.append(cols,to_predict)
data_df=df[cols]
print (data_df.head())
data_df = data_df.reset_index()
dfc = data_df.reindex(np.random.permutation(data_df.index))
dfc.fillna(value=-99999, inplace=True)
forecast_out = int(math.ceil(0.01 * len(dfc)))
dfx = dfc[features]
X = np.array(dfx)
y = np.array(dfc[to_predict])
names = np.array(dfc.columns.values)



# clf = RandomForestClassifier(n_estimators=100,n_jobs=-1)
# clf.fit(X,y)
# X_selected = clf.transform(X)
# feat_list = sorted(zip(map(lambda x: round(x, 4), clf.feature_importances_), names), 
#              reverse=True)
# print (feat_list)
# good_feats = []
# for i in feat_list:
# 	array = np.asarray(i)
# 	if array[1] == 'index':
# 		pass
# 	else:
# 		good_feats.append(array[1])

# print (good_feats)

# dfx = dfc[good_feats]
X = np.array(dfx)

eval_size = .3
kf = StratifiedKFold(y,round(1./eval_size))
train_indices, valid_indices = next(iter(kf))
X_train, y_train = X[train_indices], y[train_indices]
X_test, y_test = X[valid_indices],y[valid_indices]
#X_train, X_test, y_train, y_test = cross_validation.train_test_split(X,y,test_size = .3)

#print (data_df.describe())
# run randomized search
test_size=np.shape(X_test)[0]
print (test_size)
numbers = (.001,.01,1,10,100)
max_c=0
maxxy=0
for i in numbers:
    svc = svm.SVC(kernel='rbf',C=i).fit(X_train, y_train)
    correct_count=0
    for x in range(1, test_size+1):
        if (svc.predict(X_test[-x])[0] - y_test[-x]) == 0:
            correct_count = correct_count + 1
    print("C- " ,i, ":" ,(correct_count*100/test_size))
    if correct_count >= maxxy:
        maxxy=correct_count
        max_c=i
print (max_c)

svc = svm.SVC(kernel='rbf',C=max_c,class_weight='balanced').fit(X_train, y_train)
correct_count=0
weight = None
for x in range(1, test_size+1):
	print (X_test[-x])
	if (svc.predict(X_test[-x])[0] - y_test[-x]) == 0:
		correct_count = correct_count + 1
print("weight- Balanced:" ,(correct_count*100/test_size))
if correct_count >= maxxy:
	maxxy=correct_count
	weight='balanced'


clf= svm.SVC(kernel='rbf', C=max_c,class_weight=weight).fit(X_train, y_train)

pname = 'Classifiers/slave1_classifier.pickle'
with open(pname,'wb') as f:
	pickle.dump(clf,f)


accuracy = clf.score(X_test,y_test)



correctbuy = 0
buymiss = 0
wrongbuy = 0

for x in range(1,len(X_test)):
	temp = X_test[-x]
	temp = np.array(temp).reshape((1, -1))
	if clf.predict(temp)[0] == 1 or y_test[-x]==1 :
		if y_test[-x]==1 and  clf.predict(temp)[0] == 1:
			correctbuy = correctbuy + 1
		elif y_test[-x]==1 and  clf.predict(temp)[0] == 0:
			buymiss = buymiss +1
		elif y_test[-x]==0 and  clf.predict(temp)[0] == 1:
			wrongbuy = wrongbuy +1
	diff = y_test[-x] - clf.predict(temp)[0]

print ('Wrongbuy',wrongbuy)
print ('buymiss',buymiss)
print ('Correctbuy',correctbuy)
if buymiss == 0:
	buymiss ==1

print ('Accuracy', accuracy)
print ('Length of Dataset',len(dfc))
print ('Time in Dataset',len(dfc)/60,'hours')
print ('Number of Opportunities',data_df[data_df[to_predict]>0].count()[to_predict])
print ('Expected Profit: ', ((correctbuy)/(correctbuy+wrongbuy+buymiss)) * (df[df['prof']>0].sum()['prof']))

#this treats each row as a day and pushes it back for graphing purposes
'''
lin_svc = svm.LinearSVC(C=1).fit(X,y)
a = lin_svc.predict(XX)
ndarr = np.asarray(a) # if ndarr is actually an array, skip this
fast_df = pd.DataFrame({"new_type": ndarr.ravel()})
a.tolist()b
data_dfm['new_type'] =  fast_df['new_type']
data_dfm.to_csv('final_learned.csv')
'''