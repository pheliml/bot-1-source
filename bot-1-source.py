import websockets
import json
import pandas as pd
import asyncio
import ta
from binance.client import Client
import os

"""this is a test commit to see if it works"""
#API Keys
api_key = "h3cn0BMMedkmF9hshLwgriBtKpdi8LJfxXY5AolBPQPwCB7Cu8hT2xB91Bo8XYAk"
api_secret = "J9961dgrgDe7YHMyMPyqPVM47AG91LMAxwiDbEvugvjS0MeaC2aBPatZZ6zU30Wh"
client = Client(api_key, api_secret)
client.API_URL = 'https://testnet.binance.vision/api'


#Create Dataframe
def createframe(msg):
    df = pd.DataFrame([msg])
    #s=Symbol, E=EventTime, c=ClosingPrice
    df = df.loc[:,["s","E","c"]]
    df.columns = ["Symbol", "Time", "Price"]
    df.Price = df.Price.astype(float)
    df.Time = pd.to_datetime(df.Time, unit="ms")
    return df


#Connect to websocket
stream =\
websockets.connect("wss://testnet.binance.vision/stream?streams=ethusdt@miniTicker")


df = pd.DataFrame()
open_position = False

#Main Loop
async def main():
    async with stream as reciever:
        while True:
            data = await reciever.recv()
            data = json.loads(data)["data"]
            df = df.append(createframe(data))
            
            if len(df) >30:
                if not open_position:
                    if ta.momentum.roc(df.Price, 30).iloc[-1] > 0 and \
                    ta.momentum.roc(df.Price, 30).iloc[-2]:
                        try:
                            buy_limit = client.create_test_order(
                            symbol='ETHUSDT',
                            side='BUY',
                            type='MARKET',
                            quantity=10)
                            print(buy_limit)
                        except:
                            print(e)
                        open_position = True
                        print("Trade Placed")
            
                if open_position:
                    if len(df) > 1:
                        df["highest"] = df.Price.cummax()
                        df["trailingstop"] = df["highest"] * 0.995
                        if df.iloc[-1].Price < df.iloc[-1].trailingstop or \
                        df.iloc[-1].Price / df["highest"] > 1.002:
                            try:
                                sell_limit = client.create_test_order(
                                symbol='ETHUSDT',
                                side='SELL',
                                type='MARKET',
                                quantity=10)
                                print(sell_limit)
                            except:
                                print(e)
                            print("Option Sold")
                            open_position = False
                    
            print(df.iloc[-1])