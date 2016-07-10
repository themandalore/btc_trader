'''
Summary Statistics

'''


from sklearn import svm,preprocessing
from pandas import *
import pandas as pd
import numpy as np
from numpy import array
import os,glob
from stored import *
from preprocessing import preprocess
import matplotlib.pyplot as plt
from matplotlib import style

style.use('fivethirtyeight')

version = 'v3'

directory = 'C:\\Code\\btc\\Trader\\Data\\'
'''
Use prices.csv when ready
'''

classified =version+"_total.csv"

#enter ether quantity to trade (I'm thinking 10 lot, but this quantity could be based later on a maximized quanity)

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
        print (len(dfname.index))
        print (len(dfone.index))
        print ('Appended:',file)
        
print (len(dfone.index))
dfone = dfone.replace("NaN",-99999).replace("N/A",-99999).replace('NaT',-999999)
dfone['k_time2'] = pd.to_datetime(dfone['k_time'])
dfone['timechange']=dfone['k_time2'] - dfone['k_time2'].shift(1)
print (dfone.head())
dfone = dfone.drop(dfone[dfone['timechange'] > Timedelta('0 days 00:02:00')].index)
df = dfone.drop(dfone[dfone['timechange'] < Timedelta('0 days 00:00:01')].index)
#df=dfone.drop('k_time',1)
df=df.drop('timechange',1)
df['date_int'] = df['k_time2'].astype(np.int64)
print (df['k_time2'])
#df=df.drop('k_time2',1)
#df = df.replace("NaN",-99999).replace("N/A",-99999).replace('NaT',-999999)

df,px = preprocess(df)

df.set_index(['k_time2','k_spread'])
plt.plot(df['k_time2'],df['k_spread'])
plt.show()




'''
To find

    Volume by time in graphs
    Volatility of price over time period
    Max/min spreads

'''