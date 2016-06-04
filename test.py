import time, json, requests, csv
"""
Some api pages
https://www.kraken.com/help/api

"""

def btceDepth(info):
    btceBtcD = requests.get('https://btc-e.com/api/3/depth/eth_btc')
    quantity = 0
    print (btceBtcD.json()['eth_btc'][info])
    '''for i in btceBtcD.json()['eth_btc'][info]:
        if info == 'asks':
            bmark = btce_ETH_sell
        else: bmark = btce_ETH_buy
        if abs(i[0]-bmark) <= 1:
            quantity = quantity + i[1]
        else:
            break
'''
    return quantity

btceDepth('asks')