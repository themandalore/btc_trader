import transact
from transact import api
api = api()

import transact_k

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