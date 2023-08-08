import websockets
import json
import pandas as pd
import asyncio
import ta
from binance.client import Client
from binance.enums import *
import os
from colorama import Style, Fore
import logging 
logging.basicConfig(filename = 'file.log',
                    level = logging.INFO,
                    format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s')

print(Style.RESET_ALL)

"""Initialise the Binance API call"""
api_key = os.getenv("API_KEY")
api_secret = os.getenv("API_SECRET")

client = Client(api_key, api_secret)


"""Test API request to server"""
server_ping = client.ping()
print(server_ping)
server_status = client.get_system_status()
print(server_status)
account_status = client.get_account_api_trading_status()
print(account_status)

"""Create the websocket connection"""
stream =\
websockets.connect('wss://stream.binance.com:9443/stream?streams=ethusdt@miniTicker')

"""Create the dataframe to hold websocket information"""
def createframe(msg):
    df = pd.DataFrame([msg])
    df = df.loc[:,["s","E","c"]]
    df.columns = ["Symbol", "Time", "Price"]
    df.Price = df.Price.astype(float)
    df.Time = pd.to_datetime(df.Time, unit="ms")
    return df

"""Create empty data frame to append new incoming data from the websocket to"""
df=pd.DataFrame()

"""Main loop"""
async def main():
    sell_price = 0
    buy_price = 0
    open_position = False
    async with stream as reciever:
        while True:
            global df
            data = await reciever.recv()
            data = json.loads(data)["data"]
            df = df.append(createframe(data))
            
            if len(df) >30:
                if not open_position:
                    if ta.momentum.roc(df.Price, 30).iloc[-1] > 0 and \
                    ta.momentum.roc(df.Price, 30).iloc[-2]:
                        logging.info("Creating Buy Order")
                        # create a real order if the test orders did not raise an exception
                        try:
                            order = client.create_order(
                            symbol='ETHUSDT',
                            side='BUY',
                            type='MARKET',
                            quantity=0.07)
                            print(order)
                        except Exception as e:
                            print(e)
                            break
                        open_position = True
                        buy_price = float(order["fills"][0]["price"])
                        tether_buy_price = float(order["cummulativeQuoteQty"])
                        print(Fore.GREEN + f"Trade Placed - USDT:{tether_buy_price}")
                        logging.info("Executed Buy Order")
                        print(Style.RESET_ALL)
            
                if open_position:
                    subdf = df[df.Time >= pd.to_datetime(order["transactTime"], unit="ms")]
                    if len(subdf) > 1:
                        subdf["highest"] = subdf.Price.cummax()
                        subdf["trailingstop"] = subdf["highest"] * 0.9975
                        if subdf.iloc[-1].Price < subdf.iloc[-1].trailingstop or \
                        df.iloc[-1].Price / float(order["fills"][0]["price"]) >1.002:
                            logging.info("Creating Sell Order")
                            try:
                                order = client.create_order(
                                symbol='ETHUSDT',
                                side='SELL',
                                type='MARKET',
                                quantity=0.07)
                                print(order)
                            except Exception as e:
                                print(e)
                                break
                            sell_price = float(order["fills"][0]["price"])
                            tether_sell_price = float(order["cummulativeQuoteQty"])
                            print(Fore.GREEN + f"Trade Placed - USDT:{tether_sell_price}")
                            print(f"You made {(tether_sell_price - tether_buy_price)} profit UDST")
                            logging.info("Executed Sell Order")
                            print(Style.RESET_ALL)
                            open_position = False
                        print(subdf.iloc[-1])
            if not open_position:
                print(df.iloc[-1])

asyncio.get_event_loop().run_until_complete(main())
