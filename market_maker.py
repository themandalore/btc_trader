'''market maker program'''

from transact_cb import *
from stored import *
import numpy as np
import time, json, requests, csv, datetime
import pandas as pd

profit = 0
trade_quant = .01
#I use .01 for BTC USD
open_bids = 0 
open_asks = 0
spread_thresh = .1
order_thresh = .2
#spread_thresh is min spread, order thresh is about 2 times spread if tight
num_orders = 0
product = 'BTC/USD'
p1 = product.split('/')[0]
p2 = product.split('/')[1]
prod_string = p1+'-'+p2

x = cb_balance()
for i in x:
	if i[0]==p1:
		starting_eth_balance =float(i[1])
	if i[0] ==p2:
		starting_btc_balance = float(i[1])
quant_change = 0

s_trades = 0
for i in cb_history():
	s_trades += 1

print (cancel_all())

while True:
	time.sleep(1)
	USD, bid, ask,b_depth,a_depth,adj_imb = gdax(prod_string)
	bid = float(bid)
	ask = float(ask)
	USD = float(USD)

	change = 0
	x = cb_balance()
	for i in cb_balance():
		if i[0]==p1:
			quant_change = float(i[1]) - starting_eth_balance

	if ask - bid > 0:
		open_bids = 0
		open_asks = 0
		for i in cb_open():
			if i['side'] == 'buy':
				open_bids += 1
				bid_price = float(i['price'])
				bid_id = i['id']
			else:
				open_asks += 1
				ask_price = float(i['price'])
				ask_id = i['id']
		open_orders = open_asks + open_bids

		if quant_change <=0:
			if open_bids == 0:
				open_bid_price = ask - spread_thresh
				print ('BID PLACED',cb_trade('buy',trade_quant,open_bid_price,prod_string))
				num_orders += 1
				change = 1
			elif abs(bid-bid_price) > order_thresh:
				print ('Modification Cancel:',cancel_order(bid_id))
				open_bid_price = ask - spread_thresh
				print ('BID PLACED',cb_trade('buy',trade_quant,open_bid_price,prod_string))
				num_orders += 1
				change = 1

			else:
				pass

		if quant_change >=0:
			if open_asks == 0:
				open_ask_price = bid + spread_thresh
				print ('ASK PLACED',cb_trade('sell',trade_quant,open_ask_price,prod_string))
				num_orders +=1
				change = 1
			elif abs(ask-ask_price) > order_thresh:
				print ('Modification Cancel (Ask):',cancel_order(ask_id))
				open_ask_price = bid + spread_thresh
				print ('ASK PLACED',cb_trade('sell',trade_quant,open_ask_price,prod_string))
				num_orders +=1
				change = 1
			else:
				pass

	if change > 0:	
		x = cb_balance()
		for i in x:
			if i[0]==p1:
				ethereum = float(i[1])
			if i[0] ==p2:
				bitcoin = float(i[1])
		btc_change = starting_btc_balance - bitcoin
		eth_change = starting_eth_balance - ethereum
		total_change = btc_change + (eth_change * (bid + ask)/2) 
		num_trades = -s_trades
		for i in cb_history():
			num_trades += 1

		open_orders = 0
		for i in cb_open():
			open_orders += 1
		print ('Open Orders:',open_orders,
			'Base Profit',p2,btc_change ,
			'Subset Profit',p1,eth_change ,
			'Adj Profit',total_change,
			'Number of Trades:',num_trades,
			'Number of Orders:',num_orders,
			'Quantity Change:',quant_change)

	if abs(quant_change) > 2:
		break


'''Strategy

Spoofing strategy:
Get price level (say bid 100 ask 102) for ability to buy 100 ether (99)
place buy order of large quantity at mid point of ask to 100level (100.5)
cancel buy order and place sell order at 100.5
sell 10 at 100.5 then buy it at 100
 
'''
 