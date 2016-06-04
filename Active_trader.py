import transact, pickle
from transact import api
api = api()
import pandas as pd

import transact_k

'''
Get API stuff from the data pull (use defs)
Get Account balances
Pull in classifier
Keep track of all open orders, positions, and expected/ actual profits
'''

version = v2
imp = version + '_data'
import imp


#This gets API data

titty = []
titty.append(titles)
df = pd.DataFrame(get_data(), columns = titty)
df = preprocess(df)


#This pulls in our classifier

pname = version + '_classifier.pickle'
pickle_in = open(pname,'rb')
clf = pickle.load(pickle_in)



'''
BTCE
'''

#This gets the BTCE open orders
print(api.ActiveOrders(tpair='eth_btc'))


#This is how you trade
'''
print (api.Trade(tpair='eth_btc',ttype='buy',trate=.026,tamount=1))

'''


#This is how you cancel an order
#print (api.CancelOrder(torder_id=1084020979))

print(api.ActiveOrders(tpair='eth_btc'))

'''
Kraken 
'''

print(k_open())