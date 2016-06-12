from sklearn import svm,preprocessing
from pandas import *
import pandas as pd
import numpy as np
from numpy import array
import glob, os

version = 'v2'

directory = 'C:\\Code\\btc\\Trader\\Data\\'
'''
Use prices.csv when ready
'''
'''
os.remove(directory+version+"_total.csv")

os.chdir(directory)
fout=open(directory+version+"_total.csv","a")
for file in glob.glob(version+"_*.csv"):
    for line in open(file,'r'):
         fout.write(line) 
fout.close()

command = "copy "+directory+version+"_*.csv "+directory+version+"_total.csv"
print (command)
os.system(command)
'''
numby= 0 
frames = []
os.chdir(directory)
for file in glob.glob(version+"_*.csv"):
    numby = numby +1
    dfname='df_'+str(numby)
    dfname = pd.DataFrame.from_csv(file)
    frames.append(dfname)
    print(file)

data_dfc=pd.concat(frames)

print (data_dfc.head())