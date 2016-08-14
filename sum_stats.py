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
import matplotlib.pyplot as plt
from matplotlib import style
from matplotlib.backends.backend_pdf import PdfPages


style.use('fivethirtyeight')

version = 'v5'
inc_vers = ('v5','v4','v3')
directory = 'C:\\Code\\btc\\Trader\\Data\\'
pp = PdfPages(directory + version+'_sumstats.pdf')
'''
Use prices.csv when ready
'''
directory = 'C:\\Code\\btc\\Trader\\Data\\'
'''
Use prices.csv when ready
'''
classified = 'p_'+version + '_total.csv'

df = pd.DataFrame.from_csv(directory + classified)
df,px = preprocess(df)
print (df.head())

stime=df['k_time2'].min()
etime = df['k_time2'].max()
text1="Start Time:"+stime
text2="End Time:"+etime

plt.figure() 
plt.axis('off')
plt.text(0.1,0.9,"Summary Stats",ha='center',va='center')
plt.text(0.1,0.5,text1,ha='left',va='center')
plt.text(0.1,0.4,text2,ha='left',va='center')
plt.savefig(pp, format='pdf')
plt.clf()

data = {'Min':'Max',}
for column in df:
    d=df[column].min()
    e=df[column].max()
    data[d] = e

print (data)



#df.set_index(['k_time2','K_bid'])
df2 = df[df['k_bid_vol'] > 0]
plt.title('Kraken Bid Volume')
plt.plot(df2['k_bid_vol'],linewidth=1.0)
plt.savefig(pp, format='pdf')
plt.clf()


df2 = df[df['k_imbalance'] > -9000]
plt.title('Kraken Imbalance BTC/ETH')
plt.plot(df2['k_imbalance'],linewidth=1.0)
plt.savefig(pp, format='pdf')
plt.clf()


df2 = df[df['kprice_ma2'] > 0]
plt.title('Moving Avg BTC/ETH')
plt.plot(df2['kprice_ma2'],linewidth=1.0)
plt.savefig(pp, format='pdf')
plt.clf()

df2 = df[df['ma_diff20'] > -1000]
df2 = df2[df2['ma_diff20'] < 1000]
plt.title('Moving Avg diff (20) BTC/ETH')
plt.plot(df2['ma_diff20'],linewidth=1.0)
plt.savefig(pp, format='pdf')
pp.close()

'''
To find

    Volume by time in graphs
    Volatility of price over time period
    Max/min spreads

'''

