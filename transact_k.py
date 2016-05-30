
import krakenex
import http.client
import urllib.request, urllib.parse, urllib.error
import json
import hashlib
import hmac
import time

'''
K:

recieving all coins takes six confirmations (~ an hour) before funds are available
'''

'''
K:

recieving all coins takes six confirmations (~ an hour) before funds are available
'''
k = krakenex.API()
k.load_key('kraken.key')

def k_trade_eth(type,quantity,price):

    trade = k.query_private('AddOrder', {'pair': 'XETHXXBT',
                             'type': type,
                             'ordertype': 'limit',
                             'price': price,
                             'volume': quantity,
                             })
    return trade

def k_open():
        x = k.query_private('OpenOrders')
        return x['result']

def k_balance():
      x = k.query_private('Balance')
      return x

def k_history():
    x = k.query_private('TradesHistory')
        return x['result']

print (k_trade_eth('sell','1',.28))

print(k_balance())

print (k_open())