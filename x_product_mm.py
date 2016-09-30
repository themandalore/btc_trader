'''market maker program'''

from transact_cb import *
from stored import *
import numpy as np
import time, json, requests, csv, datetime
import pandas as pd

profit = 0
trade_quant1 = .01#I use .01 for BTC USD
spread_thresh1 = .1#spread_thresh is min spread, order thresh is about 2 times spread if tight
order_thresh1 = .2
open_bids = 0 
open_asks = 0
num_orders = 0
product = 'BTC/USD'
product2 = 'ETH/USD' #have 2 and 3 be the base of 1
product3='ETH/BTC'
p1 = product.split('/')[0]
p2 = product.split('/')[1]
p3 = product3.split('/')[0]

prod_string1 = p1+'-'+p2
prod_string2 = p3+'-'+p2
prod_string3 = p3+'-'+p1

x = cb_balance()
for i in x:
	if i[0]==p1:
		starting_p1_balance =float(i[1])
	if i[0] ==p2:
		starting_p2_balance = float(i[1])
	if i[0] ==p3:
		starting_p3_balance = float(i[1])

p1_change = 0
p2_change = 0
p3_change = 0

s_trades = 0
for i in cb_history():
	s_trades += 1

print (cancel_all())



while True:
	time.sleep(1)
	change = 0
	for i in cb_balance():
		if i[0]==p1:
			quant_change_p1 = float(i[1]) - starting_p1_balance
		elif i[0]==p2:
			quant_change_p2 = float(i[1]) - starting_p2_balance
		elif i[0]==p3:
			quant_change_p3 = float(i[1]) - starting_p3_balance

	USD, bid1,ask1,bid2,ask2,bid3,ask3 = datagrab()
	#this tells us if theres an arb op. if mbuy1, buy btc, sell for eth, sell for USD
	if ask1 < (bid2/bid3)-.0025*bid2 -.0025*bid3:
		print ('Arb number UBEU:',ask1 - (bid2/bid3))
		qee = trade_quant1/bid3
		trade_quant3 = round(float(qee),2)
		print (trade_quant3, qee)
		change = 1 
		y = 0 
		while y < 3:
			x = cb_trade('buy',trade_quant1,ask1,prod_string1)
			try:
				if x['created_at']:
					y = 3
					print ('ARB UBEU TRADE (btc usd):',x)
			except:
				print ('ERROR in ARB UBEU Trade (btc usd)',x)
				y =+ 1
		y = 0 
		while y < 3:
			x = cb_trade('sell',trade_quant3,bid3,prod_string3)
			try:
				if x['created_at']:
					y = 3
					print ('ARB UBEU TRADE (eth btc):',x)
			except:
				print ('ERROR in ARB UBEU Trade (eth btc)',x)
				y =+ 1
		y=0
		while y < 3:
			x = cb_trade('sell',trade_quant3,bid2,prod_string2)
			try:
				if x['created_at']:
					y = 3
					print ('ARB UBEU TRADE (eth usd):',x)
			except:
				print ('ERROR in ARB UBEU Trade (eth usd)',X)
				y =+ 1

		USD, bid1,ask1,bid2,ask2,bid3,ask3 = datagrab()
	if bid1 > (ask2/bid3)+.0025*ask2 +.0025*bid3:
		print ('Arb number BUEB',bid1 - (ask2/bid3))
		qee = trade_quant1/bid3
		trade_quant3 = round(float(qee),2)
		print (trade_quant3, qee)
		change = 1 
		y = 0 
		while y < 3:
			x = cb_trade('sell',trade_quant1,ask1,prod_string1)
			try:
				if x['created_at']:
					y = 3
					print ('ARB BUEB TRADE (btc usd):')
			except:
				print ('ERROR in ARB BUEB Trade (btc usd',x)
				y = y + 1
		y = 0 
		while y < 3:
			x = cb_trade('buy',trade_quant3,ask2,prod_string2)
			try:
				if x['created_at']:
					y = 3
					print ('ARB BUEB TRADE (eth usd):')
			except:
				print ('ERROR in ARB BUEB Trade (eth usd',x)
				y = y + 1
		y=0
		while y < 3:
			x = cb_trade('sell',trade_quant3,ask3,prod_string3)
			try:
				if x['created_at']:
					y = 3
					print ('ARB BUEB TRADE (btc eth):')
			except:
				print ('ERROR in ARB BUEB Trade (btc eth',x)
				y = y + 1

		USD, bid1,ask1,bid2,ask2,bid3,ask3 = datagrab()

	if ask1 - bid1 > 0:
		open_bids1 = 0
		open_asks1 = 0
		for i in cb_open():
			if i['side'] == 'buy':
				open_bids1 += 1
				bid_price1 = float(i['price'])
				bid_id1 = i['id']
			else:
				open_asks1 += 1
				ask_price1= float(i['price'])
				ask_id1 = i['id']
		open_orders1 = open_asks1 + open_bids1

		if quant_change_p1 <=0:
			if open_bids1 == 0:
				open_bid_price = round(float(ask1 - spread_thresh1),2)
				print ('BID PLACED',cb_trade('buy',trade_quant1,open_bid_price,prod_string1))
				num_orders += 1
				change = 1
			elif abs(bid1-bid_price1) > order_thresh1:
				print ('Modification Cancel:',cancel_order(bid_id1))
				open_bid_price = ask1 - spread_thresh1
				print ('BID PLACED',cb_trade('buy',trade_quant1,open_bid_price,prod_string1))
				num_orders += 1
				change = 1

			else:
				pass

		if quant_change_p1 >=0:
			if open_asks1 == 0:
				open_ask_price = bid1 + spread_thresh1
				print ('ASK PLACED',cb_trade('sell',trade_quant1,open_ask_price,prod_string1))
				num_orders +=1
				change = 1
			elif abs(ask1-ask_price1) > order_thresh1:
				print ('Modification Cancel (Ask):',cancel_order(ask_id1))
				open_ask_price = bid1+ spread_thresh1
				print ('ASK PLACED',cb_trade('sell',trade_quant1,open_ask_price,prod_string1))
				num_orders +=1
				change = 1
			else:
				pass

	if change > 0:	
		for i in cb_balance():
			if i[0]==p1:
				quant_change_p1 = float(i[1]) - starting_p1_balance
			elif i[0]==p2:
				quant_change_p2 = float(i[1]) - starting_p2_balance
			elif i[0]==p3:
				quant_change_p3 = float(i[1]) - starting_p3_balance
		total_change = quant_change_p2 + (quant_change_p1 * (bid1 + ask1)/2)+quant_change_p3*(bid3 + ask3)/2
		num_trades = -s_trades
		for i in cb_history():
			num_trades += 1

		open_orders = 0
		for i in cb_open():
			open_orders += 1
		print ('Open Orders:',open_orders,
			'USD Profit',quant_change_p2 ,
			'BTC Profit',quant_change_p1 ,
			'ETH Profit',quant_change_p3,
			'Adj Profit',total_change,
			'Number of Trades:',num_trades,
			'Number of Orders:',num_orders)

	if total_change < -.05:
		print ('Loss too high')
		break


'''Strategy

Spoofing strategy:
Get price level (say bid 100 ask 102) for ability to buy 100 ether (99)
place buy order of large quantity at mid point of ask to 100level (100.5)
cancel buy order and place sell order at 100.5
sell 10 at 100.5 then buy it at 100
 
'''
 