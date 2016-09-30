'''Master Trader'''
import os
from subprocess import *

#run child script 1

proc = Popen('python "C:\\Code\\btc\\Trader\\MarketMaker_ethusd.py"', shell=True, stdin=PIPE, stdout=PIPE)
for line in proc.stdout:
	print (line)


#run child script 2
#p = Popen([r'C:\childScript2.py', "ArcEditor"], shell=True, stdin=PIPE, stdout=PIPE)
#output = p.communicate()
#print output[0]


'''make_mark(product='ETH/BTC')
make_mark(product='ETH/USD')
arb_test()
'''
