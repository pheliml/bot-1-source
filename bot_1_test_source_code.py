import asyncio
import json
import websockets
import pandas as pd
import ta
from binance.client import Client
import logging
logging.basicConfig(filename = 'file.log',
                    level = logging.INFO,
                    format = '%(asctime)s:%(levelname)s:%(name)s:%(message)s')

#API Keys
API_KEY = "h3cn0BMMedkmF9hshLwgriBtKpdi8LJfxXY5AolBPQPwCB7Cu8hT2xB91Bo8XYAk"
API_SECRET = "J9961dgrgDe7YHMyMPyqPVM47AG91LMAxwiDbEvugvjS0MeaC2aBPatZZ6zU30Wh"
client = Client(API_KEY, API_SECRET)
client.API_URL = 'https://testnet.binance.vision/api'


"""Function to create the dataframe to store the data from the websocket"""
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

df=pd.DataFrame()

#Main Loop
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
                        try:
                            buy_limit = client.create_test_order(
                            symbol='ETHUSDT',
                            side='BUY',
                            type='MARKET',
                            quantity=10)
                            print(buy_limit)
                            buy_price = df.iloc[-1].Price
                            print(f"Buy Price: {buy_price}")
                            transact_time = df.iloc[-1].Time
                        except Exception as e:
                            print(e)
                        open_position = True
                        print(f"Trade Placed: {df.iloc[-1].Time}")
                        logging.info("Buy Order Excecuted")
                if open_position:
                    subdf = df[df.Time >= transact_time]
                    if len(subdf) > 1:
                        subdf["highest"] = subdf.Price.cummax()
                        subdf["trailingstop"] = subdf["highest"] * 0.995
                        if (subdf.iloc[-1].Price < subdf.iloc[-1].trailingstop).all() or \
                        ((df.iloc[-1].Price / buy_price) > 1.0002).all():
                            logging.info("Creating Sell Order")
                            try:
                                sell_limit = client.create_test_order(
                                symbol='ETHUSDT',
                                side='SELL',
                                type='MARKET',
                                quantity=10)
                                print(sell_limit)
                                sell_price = subdf.iloc[-1].Price
                                print(f"Option Sold at: {sell_price}")
                            except Exception as e:
                                print(e) 
                            open_position = False
                            print(f"Trade Closed: {subdf.iloc[-1].Time}")
                            print(f"Sold at: {sell_price} for a profit of {sell_price - buy_price}")
                            logging.info("Sell Order Executed")
                            #return sell_price, buy_price
    
                        print(subdf.iloc[-1])        
            if not open_position:
                print(df.iloc[-1])                                 
asyncio.get_event_loop().run_until_complete(main())
