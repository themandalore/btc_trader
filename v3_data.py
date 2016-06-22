import time, json, requests, csv, datetime, os
from time import strftime
from stored import *
"""
Some api pages
https://www.kraken.com/help/api

Get timestamps, btc_usd price for control, poloniex price, volume data

"""
version = 'v3'
date = strftime("%Y-%m-%d")
directory = 'C:\\Code\\btc\\Trader\\'

titles =  ('obs','btce_ETH_buy','btce_ETH_sell',
    'btce_ETH_depth_bid','btce_ETH_depth_ask','K_bid'
    ,'k_ask','k_time','k_bid_vol','k_ask_vol','uc_trans',
    'okbuy','oksell','okcny','okadepth','okbdepth')
print (titles)
name = 'Data/' + version + '_' + date + '.csv'
name2='Data/building_data.csv'
with open(directory+name2, 'w') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(titles)   
    while True:
        x = x + 1
        x,btce_ETH_buy,btce_ETH_sell,btce_ETH_depth_bid,btce_ETH_depth_ask,krakenETH_bid,krakenETH_ask,k_time,k_bid_vol,k_ask_vol,uc_transokbuy,oksell,okcny,okadepth,okbdepth = get_data()
        outstring = (int(x),float(btce_ETH_buy),float(btce_ETH_sell),float(btce_ETH_depth_bid),float(btce_ETH_depth_ask),float(krakenETH_bid),float(krakenETH_ask),k_time,float(k_bid_vol),float(k_ask_vol),float(uc_trans),float(okbuy),float(oksell),float(okcny),float(okadepth),float(okbdepth))
        spamwriter.writerow(outstring)
        print (outstring)
        time.sleep(5) # 120 equals two minutes
        if date != strftime("%Y-%m-%d"):
            break

os.rename(directory+name2,directory+name)

print ('Errors:', errors)