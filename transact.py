
import krakenex
import http.client
import urllib.request, urllib.parse, urllib.error
import json
import hashlib
import hmac
import time


f = open('btce.key', "r")
btcekey = f.readline().strip()
btce_secret = f.readline().strip()


'''get def 
get latency of each type
now optimize data based on latency of each
'''

'''
BTCE:
recieving all coins (recorded a few minutes after 3 confirmations ~ 35 minutes for BTC and ETH)
~1 to 2 second delay on orders, but pretty good
'''

class api:
 __api_key  = btcekey
 __api_secret   = btce_secret
 __nonce_v  = 1;
 __wait_for_nonce = True

 def __init__(self,api_key=__api_key,api_secret=__api_secret,wait_for_nonce=__wait_for_nonce):
  self.__api_key = api_key
  self.__api_secret = api_secret
  self.__wait_for_nonce = wait_for_nonce

 def __nonce(self):
   if self.__wait_for_nonce: time.sleep(1)
   self.__nonce_v = str(time.time()).split('.')[0]

 def __signature(self, params):
  sig = hmac.new(self.__api_secret.encode(), params.encode(), hashlib.sha512)
  return sig.hexdigest()

 def __api_call(self,method,params):
  self.__nonce()
  params['method'] = method
  params['nonce'] = str(self.__nonce_v)
  params = urllib.parse.urlencode(params)
  headers = {"Content-type" : "application/x-www-form-urlencoded",
                      "Key" : self.__api_key,
             "Sign" : self.__signature(params)}
  conn = http.client.HTTPSConnection("btc-e.com")
  conn.request("POST", "/tapi", params, headers)
  response = conn.getresponse().read().decode()
  data = json.loads(response)
  conn.close()
  return data
  
 def get_param(self, couple, param):
  conn = http.client.HTTPSConnection("btc-e.com")
  conn.request("GET", "/api/2/"+couple+"/"+param)
  response = conn.getresponse().read().decode()
  data = json.loads(response)
  conn.close()
  return data

 def ActiveOrders(self, tpair):
  params = { "pair" : tpair }
  return self.__api_call('ActiveOrders', params)
#ActiveOrders(self,eth_btc)
 def Trade(self, tpair, ttype, trate, tamount):
  params = {
   "pair"   : tpair,
   "type"   : ttype,
   "rate"   : trate,
   "amount" : tamount}
  return self.__api_call('Trade', params)
  
 def CancelOrder(self, torder_id):
  params = { "order_id" : torder_id }
  return self.__api_call('CancelOrder', params)

