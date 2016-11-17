 
import sys
import time, json, requests, csv, datetime
import pandas as pd
import numpy as np
 
 
url="https://api.gdax.com"
product_id="BTC-USD"
 
today = datetime.datetime.now()

 
 
 
titles = ('time','low','high','open','close','volume')

 
 
def getProductHistoricRates(product='', start='', end='', granularity=''):
	payload = { "start" : start, "end" : end,"granularity" : granularity}
	response = requests.get(url + '/products/%s/candles' % (product), params=payload)
	return response.json()
	 

def getdata(granul):
	lenny=1
	x=0
	y=0
	three_hours = datetime.timedelta(minutes=3*granul)
	name = 'gdax_'+ str(granul) +'.csv'
	with open(name,'w') as fd:
			writer = csv.writer(fd)
			writer.writerow(['time','low','high','open','close','volume'])
	while lenny > 0 or y<30:
		x = x + 1
		tdelta = datetime.timedelta(minutes=3 *x *granul)
		endtime = today - tdelta
		starttime = endtime - three_hours
		try:
			all_data =[]
			data = getProductHistoricRates(product=product_id,start=starttime,end=endtime,granularity=granul)
			for i in data:
				try:
					all_data.append(i)
					y = 0
				except:
					pass
			with open(name,'a') as fd:
				for j in all_data:
					writer = csv.writer(fd)
					writer.writerow(j)
			y = y + 1
			lenny = len(data)
		except:
			pass
		if lenny == 0:
			y = y + 1
		print ('Data:',lenny,'_',starttime,'_',endtime)
		time.sleep(1)

	print ('y=',y)

'''
Next, fill in seconds that are missing in the data
'''
#getdata(60)
directory = 'C:\\Code\\btc\\Trader\\'
name = directory+'gdax_'+ str(60) +'.csv'
print (name)
df = pd.read_csv(name,error_bad_lines=False)
df = pd.DataFrame(df)
print(df.head())
df['time']=pd.to_datetime(df['time'],unit='s')
print (df.head())
print (len(df))
df.to_csv(name)
print (starttime,'to',today)