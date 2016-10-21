 
import sys
import time, json, requests, csv, datetime
import pandas as pd
import numpy as np
 
 
url="https://api.gdax.com"
product_id="BTC-USD"
 
today = datetime.datetime.now()
three_hours = datetime.timedelta(minutes=3)
 
 
 
titles = ('time','low','high','open','close','volume')
all_data =[]
 
 
def getProductHistoricRates(product='', start='', end='', granularity=''):
	payload = { "start" : start, "end" : end,"granularity" : granularity}
	response = requests.get(url + '/products/%s/candles' % (product), params=payload)
	return response.json()
	 
lenny=1
x=0
y=0
while lenny > 0 or y<20:
	x = x + 1
	tdelta = datetime.timedelta(minutes=3 *x)
	endtime = today - tdelta
	starttime = endtime - three_hours
	try:
		data = getProductHistoricRates(product=product_id,start=starttime,end=endtime,granularity=1)
		for i in data:
			try:
				all_data.append(i)
				y = 0
			except:
				pass
	except:
		y = y + 1
	lenny = len(data)
	if lenny == 0:
		y = y + 1
	print ('Data:',lenny,'_',starttime,'_',endtime)
	time.sleep(1)

print ('y=',y)
try:
	df = pd.DataFrame(all_data,columns=titles)
except:
	try:
		df = pd.DataFrame(all_data)
	except:
		np.savetxt("array_cb_sec.csv", all_data, delimiter=",")

df['time']=pd.to_datetime(df['time'],unit='s')
print (df.head())
print (len(df))
df.to_csv('coinbase_data_sec.csv')
print (starttime,'to',today)

'''
Next, fill in seconds that are missing in the data
'''