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

version = 'v4'
inc_vers = ('v4','v3')
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



plt.figure() 
plt.axis('off')
plt.text(0.5,0.5,"Summary Stats",ha='center',va='center')
plt.savefig(pp, format='pdf')
plt.clf()


#df.set_index(['k_time2','K_bid'])
df2 = df[df['k_bid_vol'] > 0]
plt.title('Kraken Bid Volume')
plt.plot(df2['k_bid_vol'])
plt.savefig(pp, format='pdf')
plt.clf()


df2 = df[df['k_imbalance'] > -9000]
plt.title('Kraken Imbalance BTC/ETH')
plt.plot(df2['k_imbalance'])
plt.savefig(pp, format='pdf')
plt.clf()


df2 = df[df['kprice_ma2'] > 0]
plt.title('Moving Avg BTC/ETH')
plt.plot(df2['kprice_ma2'])
plt.savefig(pp, format='pdf')
pp.close()


'''
To find

    Volume by time in graphs
    Volatility of price over time period
    Max/min spreads

'''

