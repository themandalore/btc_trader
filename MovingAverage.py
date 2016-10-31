'''market maker program'''

from transact_cb import *
from stored import *
import numpy as np
import time, json, requests, csv, datetime
import pandas as pd

'''
Get ma quantity to replace 0 as base quantity
Get orig_price of asset to calculate profit and loss based on total value and totalvalue vs market value (if mkt loses)


'''
class MarketMaker:
 
 
	def make_mark(self,product,trade_quant,spread_thresh,order_thresh):
		profit = 0
		open_bids = 0 
		open_asks = 0
		#spread_thresh is min spread, order thresh is about 2 times spread if tight
		num_orders = 0
		p1 = product.split('/')[0]
		p2 = product.split('/')[1]
		prod_string = p1+'-'+p2
		ma_quantity = 0
		ma_level = 30 #enter seconds for malevel
		x = cb_balance()
		for i in x:
			if i[0]=='USD':
				starting_usd_balance =float(i[1])
			if i[0] =='BTC':
				starting_btc_balance = float(i[1])
		quant_change = 0
		breaker = 0
		while True:
			if breaker==1:
				break
			print (cancel_all())
			zzz=0
			heartbeat=1
			USD, bid, ask,b_depth,a_depth,adj_imb = gdax(prod_string)
			if USD ==0:
				break
			start_price = float(USD)
			titles = ('time','low','high','open','close','volume')
			init_time = 0
			hist_data = []
			print ('wait' ,ma_level,'...')
			while init_time <= ma_level:
				USD = float(USD)
				hist_data.append(USD)
				time.sleep(1)
				init_time = init_time + 1
				USD, bid, ask,b_depth,a_depth,adj_imb = gdax(prod_string)
				if USD == 0:
					break
			last_values = hist_data[-ma_level:]
			ma_price = np.sum(last_values)/ma_level
			while True and zzz==0:
				heartbeat=heartbeat+1
				if heartbeat ==10:
					print ('.',spread,ma_quantity)
					heartbeat=1
				time.sleep(1)
				USD, bid, ask,b_depth,a_depth,adj_imb = gdax(prod_string)
				if USD == 0:
					break
				bid = float(bid)
				ask = float(ask)
				USD = float(USD)
				spread = max(spread_thresh,(ask-bid-spread_thresh*5))
				hist_data.append(USD)
				last_values = hist_data[-ma_level:]
				ma_price = np.sum(last_values)/ma_level
				'''Currently ma_quantity is just one of the trade_quant, if volume and trades are high enough, this can increase'''
				if USD - ma_price > 0:
					ma_quantity = -trade_quant*2
				elif USD- ma_price < 0:
					ma_quantity = trade_quant*2
				else:
					ma_quantity = 0
					
				change = 0
				x = cb_balance()
				if x == 'ERROR':
					break
				for i in cb_balance():
					if i[0]=='BTC':
						quant_change = float(i[1]) - starting_btc_balance

				if ask - bid > 0:
					open_bids = 0
					open_asks = 0
					x = cb_open()
					if x =='ERROR':
						break
					for i in x:
						if i['side'] == 'buy':
							open_bids += 1
							bid_price = float(i['price'])
							bid_id = i['id']
						else:
							open_asks += 1
							ask_price = float(i['price'])
							ask_id = i['id']
					open_orders = open_asks + open_bids

					if quant_change <=ma_quantity:
						if open_bids == 0:
							open_bid_price = round(float(ask),2)
							print ('BID PLACED',cb_trade_agg('buy',trade_quant,open_bid_price,prod_string))
							num_orders += 1
							if num_orders > 1:
								num_trades += 1
							change = 1
						elif abs(bid-bid_price) > order_thresh:
							print ('Modification Cancel:',cancel_order(bid_id))
							open_bid_price = ask - round(float(ask),2)
							print ('BID PLACED',cb_trade_agg('buy',trade_quant,open_bid_price,prod_string))
							num_orders += 1
							change = 1

						else:
							pass
					elif quant_change > ma_quantity:
						if open_bids > 0:
							print ('MA Cancel:',cancel_order(bid_id))

					if quant_change >=ma_quantity:
						if open_asks == 0:
							open_ask_price = round(float(bid),2)
							print ('ASK PLACED',cb_trade_agg('sell',trade_quant,open_ask_price,prod_string))
							num_orders +=1
							change = 1
						elif abs(ask-ask_price) > order_thresh:
							print ('Modification Cancel (Ask):',cancel_order(ask_id))
							open_ask_price = round(float(bid),2)
							print ('ASK PLACED',cb_trade_agg('sell',trade_quant,open_ask_price,prod_string))
							num_orders +=1
							change = 1
						else:
							pass
					elif quant_change < ma_quantity:
						if open_asks > 0:
							print ('MA Cancel:',cancel_order(ask_id))

				if change > 0:	
					x = cb_balance()
					if x == 'ERROR':
						break
					for i in x:
						if i[0]=='USD':
							USD_balance = float(i[1])
						if i[0] =='BTC':
							bitcoin = float(i[1])
					btc_change = bitcoin-starting_btc_balance 
					usd_change = USD_balance-starting_usd_balance
					total_change = usd_change + (btc_change * (bid + ask)/2)
					num_trades=0
					for i in cb_history():
						num_trades = num_trades + 1

					static_p_balance = USD_balance + bitcoin * start_price
					market_rate = starting_usd_balance + starting_btc_balance*(bid+ask)/2
					versus_mkt = USD_balance + bitcoin*USD - market_rate
					open_orders = 0
					x = cb_open()
					if x =='ERROR':
						break
					for i in x:
						open_orders += 1
					print ('Open Orders:',open_orders,
						'Base Profit - USD',usd_change ,
						'Subset Profit - BTC',btc_change ,
						'Adj Profit',total_change,
						'Versus Market',versus_mkt,
						'Number of Trades:',num_trades,
						'Number of Orders:',num_orders,
						'Quantity Change:',quant_change)

				if abs(btc_change) > .1 or total_change < -.1 or abs(usd_change)>30:
					breaker=1
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
mm.make_mark('BTC/USD',.02,.02,.2)