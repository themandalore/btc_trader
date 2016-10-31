'''
Take cb data and figure out:
Best time frame for moving average prediction
-apply to market making program
then do:
machine learning for price prediction
'''
import pandas as pd
import numpy as np
import datetime

directory = 'C:\\Code\\btc\\Trader\\Data\\'


def min_anal():
	df = pd.DataFrame.from_csv(directory + 'coinbase_data_sec_fmt.csv')
	df['time'] = pd.to_datetime(df['time'])
	df['price'] = (df.low + df.high)/2
	time_range = [240,480,1000,10000]
	fee = .0025
	test_range =[2,5,10,20,50]
	for j in test_range:
		for i in time_range:
			n1 = 'p_delta_'+ str(i)
			n2 = 'ma_'+str(i)
			n3='ma_diff_'+str(i)
			n4='own_ma_'+str(i)
			df[n1] = df.price - df.price.shift(i)
			df[n2] = pd.rolling_mean(df.price,i)
			df[n3] = df.price -df[n2]
			df[n4] = df.apply(lambda x : x['p_delta_1'] if  x[n3] > j else 0,axis = 1)
			df['dummy_n4'] = df.apply(lambda x : 1 if  x[n3] > j else 0,axis = 1)
			df['dummy2'] =df['dummy_n4']-df['dummy_n4'].shift(1)
			df['cost'] = df.apply(lambda x : x['price']*fee if x['dummy2'] > 0 else 0,axis = 1)
			maxtime = df['time'].max()
			mintime = df['time'].min()
			time_delta = maxtime-mintime
			prof = df[n4].sum(axis=0)
			scount = df['dummy_n4'].sum(axis=0)
			cost = df['cost'].sum(axis=0)
			Adj_prof = prof - cost
			print ('Test Range ', j,' Profit: ',i,' : ',prof,' | Daily:',prof/time_delta.days, '  Adj_prof: ',Adj_prof , 'tradecount ',scount)

	'''time_delta.days '''
	df = df.dropna()
	print ('Obs:',len(df))
	print (df.head())



def sec_anal():
	df2 = pd.DataFrame.from_csv(directory + 'coinbase_data_sec.csv')
	df2['time'] = pd.to_datetime(df2['time'],unit='s', format ='%Y-%m-%dT%H:%M:%S')
	df2.dropna()
	mintime = df2['time'].min()
	today = df2['time'].max()
	print (df2.tail())
	#today = datetime.datetime.now().replace(microsecond=0)
	tdelta = datetime.timedelta(seconds=1)
	time_data = []
	j=0
	time = today
	while time >= mintime:
		time = today - tdelta * j
		time_data.append(time)
		j = j + 1

	df3 = pd.DataFrame(time_data,columns=['time'])

	df3['time']=pd.to_datetime(df3['time'],unit='s', format ='%Y-%m-%dT%H:%M:%S')
	res = pd.merge(df3,df2, on='time', how='left')
	res.fillna(0, inplace=True)
	print (res.head())
	collist = ('low','high','open','close')
	for i in collist:
		#res[i]=res[i].astype(int)
		minny = res[i].min(axis=0)
		print (minny)
		y = 1
		while minny < 1:
			res['h2']=res[i].shift(y)
			res[i]= res.apply(lambda x : x[i] if  x[i] > 0 else x['h2'],axis = 1)
			minny = res[i].min(axis=0)
			y = y + 1
	return res
# res = sec_anal()
# print (res.head())
# print (res.tail())

# print (len(res))
# res.to_csv('coinbase_data_sec_fmt.csv')

min_anal()