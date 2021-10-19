# Import the requests library
import requests
import hmac
import hashlib
import time
import os
from telegram_send import send
from dotenv import load_dotenv

load_dotenv()

buySell = "Activating"
API_KEY = "bVwYdrmNzDkDP82WU4fpcv"
SECRET_KEY = os.environ['BOTAPIS']
cryptoURL = "https://api.crypto.com/v2/"
# Define endpointq
def startBot():
    testBuy()
try:
    endpoint = "https://api.taapi.io/bulk"

    # Define a JSON body with parameters to be sent to the API
    parameters = {
        "secret": os.environ['TAAPI'],
        "construct": {
            "exchange": "binance",
            "symbol": "XRP/USDT",
            "interval": "5m",
            "indicators": [
                {
                    "indicator": "candle"
                },{
                    "indicator": "macd",
                    "optInSignalPeriod":30
                }
            ]
        }
    }


    def testBuy():
        print(SECRET_KEY)
        buySell = "BUY"
        USDT = getSummary("USDT")
        USDTBalance = USDT["result"]["accounts"][0]["balance"]
        if USDTBalance < 1.5:
            testSell()
        response = requests.post(url=endpoint, json=parameters)
        result = response.json()

        candle = result["data"][0]["result"]["close"]
        advice = result["data"][1]["result"]["valueMACDHist"]
        if advice<=-0.0020:
            file1 = open("stoploss.txt", "w")
            file1.write("0")
            file1.close()
            file1 = open("takeprofit.txt", "r")
            check = file1.read()
            file1.close()
            price = round(candle + (candle * 0.0025), 4)
            if price<float(check):
                done=cancel()
                oke= orderStop(buySell, USDTBalance, price)
                file2 = open("takeprofit.txt", "w")
                file2.write(str(price))
                file2.close()
                coins = USDTBalance / price
                send(messages=["Bought " + str(coins) + " XRP for " + str(price) + "."])

    def testSell():
        buySell = "SELL"
        XRP = getSummary("XRP")
        XRPBalance = XRP["result"]["accounts"][0]["balance"]
        if XRPBalance < 1.5:
            testBuy()
        response = requests.post(url=endpoint, json=parameters)
        result = response.json()
        candle = result["data"][0]["result"]["close"]
        advice = result["data"][1]["result"]["valueMACDHist"]
        print(advice)
        if advice>=0.0015 :
            file1 = open("takeprofit.txt", "w")
            file1.write("1000000000")
            file1.close()
            file1 = open("stoploss.txt", "r")
            check = file1.read()
            file1.close()
            price = round(candle - (candle * 0.0025), 4)
            if price>float(check):
                done=cancel()
                oke= orderStop(buySell, XRPBalance, price)
                file2 = open("stoploss.txt", "w")
                file2.write(str(price))
                file2.close()
                money = (XRPBalance * price)
                send(messages=["Sold " + str(XRPBalance) + " XRP for " + str(price) + ". Your balance is: " + str(money)])



    def getSummary(COIN):
        req = {
            "id": 11,
            "method": "private/get-account-summary",
            "api_key": API_KEY,
            "params": {
                "currency": COIN
            },
            "nonce": int(time.time() * 1000)
        }

        # First ensure the params are alphabetically sorted by key
        paramString = ""

        if "params" in req:
            for key in sorted(req['params']):
                paramString += key
                paramString += str(req['params'][key])

        sigPayload = req['method'] + str(req['id']) + req['api_key'] + paramString + str(req['nonce'])

        req['sig'] = hmac.new(
            bytes(str(SECRET_KEY), 'utf-8'),
            msg=bytes(sigPayload, 'utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        response = requests.post(cryptoURL + "private/get-account-summary", json=req)

        return response.json()


    def order(buySell, coins):
        rCoins = int(round(coins -1, 2))
        req = {
            "id": 12,
            "method": "private/create-order",
            "api_key": API_KEY,
            "params": {
                "instrument_name": "XRP_USDT",
                "side": buySell,
                "type": "MARKET",
                "quantity": rCoins
            },
            "nonce": int(time.time() * 1000)
        }
        # First ensure the params are alphabetically sorted by key
        paramString = ""

        if "params" in req:
            for key in sorted(req['params']):
                paramString += key
                paramString += str(req['params'][key])

        sigPayload = req['method'] + str(req['id']) + req['api_key'] + paramString + str(req['nonce'])

        req['sig'] = hmac.new(
            bytes(str(SECRET_KEY), 'utf-8'),
            msg=bytes(sigPayload, 'utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        response = requests.post(cryptoURL + "private/create-order", json=req)

        return response.json()

    def orderStop(buySell, coins, price):
        rCoins = int(round(coins -0.8, 2))
        req = {
            "id": 12,
            "method": "private/create-order",
            "api_key": API_KEY,
            "params": {
                "instrument_name": "XRP_USDT",
                "side": buySell,
                "type": "STOP_LOSS",
                "trigger_price": price,
                "quantity": rCoins
            },
            "nonce": int(time.time() * 1000)
        }
        # First ensure the params are alphabetically sorted by key
        paramString = ""

        if "params" in req:
            for key in sorted(req['params']):
                paramString += key
                paramString += str(req['params'][key])

        sigPayload = req['method'] + str(req['id']) + req['api_key'] + paramString + str(req['nonce'])

        req['sig'] = hmac.new(
            bytes(str(SECRET_KEY), 'utf-8'),
            msg=bytes(sigPayload, 'utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        response = requests.post(cryptoURL + "private/create-order", json=req)

        return response.json()


    def cancel():
        req = {
            "id": 12,
            "method": "private/cancel-all-orders",
            "api_key": API_KEY,
            "params": {
                "instrument_name": "XRP_USDT"
            },
            "nonce": int(time.time() * 1000)
        }
        # First ensure the params are alphabetically sorted by key
        paramString = ""

        if "params" in req:
            for key in sorted(req['params']):
                paramString += key
                paramString += str(req['params'][key])

        sigPayload = req['method'] + str(req['id']) + req['api_key'] + paramString + str(req['nonce'])

        req['sig'] = hmac.new(
            bytes(str(SECRET_KEY), 'utf-8'),
            msg=bytes(sigPayload, 'utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        response = requests.post(cryptoURL + "private/cancel-all-orders", json=req)

        return response.json()

    startBot()
except :
    done=0