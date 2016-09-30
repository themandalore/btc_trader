'''market maker program'''

from transact_cb import *
from stored import *
import numpy as np
import time, json, requests, csv, datetime
import pandas as pd


class MarketMaker:
	def make_mark(self,product,trade_quant,spread_thresh,order_thresh):
		profit = 0
		#I use .01 for BTC USD
		open_bids = 0 
		open_asks = 0
		#spread_thresh is min spread, order thresh is about 2 times spread if tight
		num_orders = 0
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


	def arb_test(self):
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

	def datagrab(self):
		USD = float(USD_gdax())
		bid1, ask1 = mmgdax(prod_string1)
		bid1 = float(bid1)
		ask1 = float(ask1)
		bid2, ask2 = mmgdax(prod_string2)
		bid2 = float(bid2)
		ask2 = float(ask2)
		bid3, ask3 = mmgdax(prod_string3)
		bid3 = float(bid3)
		ask3 = float(ask3)
		return USD, bid1,ask1,bid2,ask2,bid3,ask3 

mm= MarketMaker()
mm.make_mark('BTC/USD',.02,.05,.2)