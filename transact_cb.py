
import json, hmac, hashlib, time, requests, base64
from requests.auth import AuthBase


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
			'CB-ACCESS-SIGN': signature_b64,
			'CB-ACCESS-TIMESTAMP': timestamp,
			'CB-ACCESS-KEY': self.api_key,
			'CB-ACCESS-PASSPHRASE': self.passphrase,
			'Content-Type': 'application/json'
		})
		return request


def load_key(path):
	f = open(path, "r")
	key = f.readline().strip()
	secret = f.readline().strip()
	API_PASS = f.readline().strip()
	return key, secret, API_PASS


		
api_url = 'https://api.gdax.com/'
API_KEY,API_SECRET,API_PASS = load_key('coinbase.key')
API_KEY.encode('utf-8')
API_PASS.encode('utf-8')
auth = CoinbaseExchangeAuth(API_KEY, API_SECRET, API_PASS)
print (auth)

def cb_trade_eth(type,quantity,price):

	order = {
	'size': 1.0,
	'price': 1.0,
	'side': 'buy',
	'product_id': 'BTC-USD',
	}
	r = requests.post(api_url + 'orders', json=order, auth=auth)
	x = r.json()
	return x

def cb_open():
	r = requests.post(api_url + 'orders', auth=auth)
	x = r.json()
	return x


def cb_balance():
	balances = []
	r = requests.get(api_url + 'accounts', auth=auth)
	x = r.json()
	for i in x:
		y = (i['currency'],i['balance'])
		balances.append(y)
	return balances


def cb_history():
	accounts =[]
	history =[]
	r = requests.post(api_url + 'accounts', auth=auth)
	x = r.json()
	for i in x:
		if i['balance']>0:
			accounts.append(i['id'])
	for i in accounts:
		r = requests.post(api_url + 'accounts/' + i +'/ledger', auth=auth)
		x = r.json()
		history.append(x)
	return history


print (cb_balance())

#print (k_trade_eth('sell','1',.28))

#print(k_balance())

#print (k_open())