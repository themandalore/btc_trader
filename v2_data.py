import time, json, requests, csv, datetime
from time import strftime
"""
Some api pages
https://www.kraken.com/help/api

Get timestamps, btc_usd price for control, poloniex price, volume data

"""
version = 'v2'
date = strftime("%Y-%m-%d")
errors = 0

def btceBU(info):
    btceBtcTick = requests.get('https://btc-e.com/api/2/eth_btc/ticker')
    return btceBtcTick.json()['ticker'][info] # replace last with updated etc


def btceDepth(info):
    btceBtcD = requests.get('https://btc-e.com/api/3/depth/eth_btc')
    quantity = 0
    btce_ETH_buy = float(btceBU('buy'))
    btce_ETH_sell = float(btceBU('sell'))
    for i in btceBtcD.json()['eth_btc'][info]:
        if info == 'asks':
            bmark = btce_ETH_sell
        else: bmark = btce_ETH_buy
        if abs(i[0]-bmark) <= 1:
            quantity = quantity + i[1]
        else:
            break

    return quantity


def kraken():
    krakenTick = requests.post('https://api.kraken.com/0/public/Depth',data=json.dumps({"pair":"XETHXXBT"}),
    headers={"content-type":"application/json"})
    try: 
        return krakenTick.json()['result']['XETHXXBT']
    except:
        errors = errors + 1
        totals = -99999999
        return total

def toshi_ut():
    toshi_block = requests.get('https://bitcoin.toshi.io/api/v0/transactions/unconfirmed')
    #   totals = toshi_block.json()['inputs']['amount'] + totals
    #for i in toshi_block.json()
    totals = 0 
    try:
        for i in toshi_block.json():
            totals = totals + i['amount']
        return totals
    except:
        errors = errors + 1
        totals = -99999999
        return total

def get_data():
    btce_ETH_buy = float(btceBU('buy'))
    btce_ETH_sell = float(btceBU('sell'))
    btce_ETH_depth_bid = float(btceDepth('bids'))
    btce_ETH_depth_ask = float(btceDepth('asks'))
    k_data =  kraken()
    krakenETH_bid= float(k_data['bids'][0][0])
    krakenETH_ask= float(k_data['asks'][0][0])
    k_time = strftime("%Y-%m-%d %H:%M:%S")
    k_bid_vol = float(k_data['bids'][0][1])
    k_ask_vol= float(k_data['asks'][0][1])
    uc_trans = float(toshi_ut())
    outstring = (x,btce_ETH_buy,btce_ETH_sell,btce_ETH_depth_bid,btce_ETH_depth_ask,krakenETH_bid,krakenETH_ask,k_time,k_bid_vol,k_ask_vol,uc_trans)
    return outstring

titles =  ('obs','btce_ETH_buy','btce_ETH_sell','btce_ETH_depth_bid','btce_ETH_depth_ask','K_bid','k_ask','k_time','k_bid_vol','k_ask_vol','uc_trans')
print (titles)
x=0
name = 'Data/' + version + '_' + date + '.csv'
with open(name, 'w') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(titles)   
    while True:
        x = x + 1
        outstring = get_data()
        spamwriter.writerow(outstring)
        print (outstring)
        time.sleep(5) # 120 equals two minutes
        if date != strftime("%Y-%m-%d"):
            break

print ('Errors:', errors)