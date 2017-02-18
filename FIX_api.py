
import json, hmac, hashlib, time, requests, base64
from requests.auth import AuthBase
from datetime import datetime,date,timedelta

# Create custom authentication for Exchange
class CoinbaseExchangeAuth(AuthBase):
	def __init__(self, api_key, secret_key, passphrase):
		self.api_key = api_key
		self.secret_key = secret_key
		self.passphrase = passphrase

	def __call__(self, request):
		timestamp = str(time.time())
		message = timestamp + request.method + request.path_url + (request.body or '')
		message = message.encode('ascii')
		hmac_key = base64.b64decode(self.secret_key)
		signature = hmac.new(hmac_key, message, hashlib.sha256)
		signature_b64 = base64.b64encode(signature.digest())
		request.headers.update({
		    'Content-Type': 'Application/JSON',
		    'CB-ACCESS-SIGN': signature_b64,
		    'CB-ACCESS-TIMESTAMP': timestamp,
		    'CB-ACCESS-KEY': self.api_key,
		    'CB-ACCESS-PASSPHRASE': self.passphrase
		})
		return request



def load_key(path):
	f = open(path, "r")
	key = f.readline().strip()
	secret = f.readline().strip()
	API_PASS = f.readline().strip()
	return key, secret, API_PASS

	
api_url = 'https://api.gdax.com/'

def auth():	
	API_KEY,API_SECRET,API_PASS = load_key('coinbase.key')
	API_KEY.encode('utf-8')
	API_PASS.encode('utf-8')
	auth = CoinbaseExchangeAuth(API_KEY, API_SECRET, API_PASS)
	return auth


def cb_trade(otype,quantity,price,product):

	'''otype = buy or sell '''

	order = {
	'size': quantity,
	'price': price,
	'side': otype,
	'product_id': product,
	'post_only': True,
	}
	r = requests.post(api_url + 'orders',data=json.dumps(order),auth=auth())
	x = r.json()
	return x

def cb_trade_agg(otype,quantity,price,product):

	'''otype = buy or sell '''

	order = {
	'size': quantity,
	'price': price,
	'side': otype,
	'product_id': product
	}
	r = requests.post(api_url + 'orders', json=order, auth=auth())
	print (r)
	x = r.json()
	print (x)
	return x

def cancel_all():
	try:
		r = requests.delete(api_url +'orders',auth=auth())
		x = r.json()
	except:
		print ('Cancel Error')
		x = 0
	return x

def cancel_order(id):
	r = requests.delete(api_url +'orders/'+ id,auth=auth())
	x = r.json()
	return x

