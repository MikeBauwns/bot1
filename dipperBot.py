# Import the requests library
from ctypes import sizeof
import requests
import hmac
import hashlib
import time
import os
from telegram_send import send
from dotenv import load_dotenv

load_dotenv()

buySell = "Activating"
API_KEY = "YghNuUJvcKMZ9KQRe29V4n"
SECRET_KEY = os.environ['BOTAPIS']
cryptoURL = "https://api.crypto.com/v2/"
# Define endpointq
def startBot():
    testBuy()
try:
    def getCandel():
        
        response = requests.get(cryptoURL + "public/get-candlestick?instrument_name=CRO_USDT&timeframe=5m")
        data= response.json()
        price_data=data["result"]["data"]
        
        size=len(price_data)
        index = size-1
        current_price=price_data[index]["c"]
        return current_price


    def testBuy():
        buySell = "BUY"
        USDT = getSummary("USDT")
        USDTBalance = USDT["result"]["accounts"][0]["balance"]
        if USDTBalance < 1.5:
            testSell()
        result = getCandel()
        file1 = open("soldAt.txt", "r")
        strsold = file1.read()
        soldAt=float(strsold)
        file1.close()

        if result<=soldAt-(soldAt*0.11):
            print("test")
            file1 = open("stoploss.txt", "w")
            file1.write("0")
            file1.close()
            file1 = open("boughtAt.txt", "w")
            file1.write(str(result))
            file1.close()
            file1 = open("takeprofit.txt", "r")
            check = file1.read()
            file1.close()
            price = round(result + (result * 0.01), 4)
            if price<float(check):
                done=cancel()
                oke= orderStop(buySell, USDTBalance, price)
                file2 = open("takeprofit.txt", "w")
                file2.write(str(price))
                file2.close()
                coins = USDTBalance / price
                send(messages=["Bought " + str(coins) + " CRO for " + str(price) + "."])

    def testSell():
        buySell = "SELL"
        CRO = getSummary("CRO")
        CROBalance = CRO["result"]["accounts"][0]["balance"]
        
        result = getCandel()
        file1 = open("boughtAt.txt", "r")
        strboughtAt = file1.read()
        file1.close()

        boughtAt=float(strboughtAt)

        if result>=boughtAt+(boughtAt*0.11):
            print('test')
            file1 = open("takeprofit.txt", "w")
            file1.write("1000000000")
            file1.close()
            file1 = open("soldAt.txt", "w")
            file1.write(str(result))
            file1.close()
            file1 = open("stoploss.txt", "r")
            check = file1.read()
            file1.close()
            price = round(result - (result * 0.01), 4)
            if price>float(check):
                done=cancel()
                oke= orderStop(buySell, CROBalance, price)
                file2 = open("stoploss.txt", "w")
                file2.write(str(price))
                file2.close()
                money = (CROBalance * price)
                send(messages=["Sold " + str(CROBalance) + " XRP for " + str(price) + ". Your balance is: " + str(money)])



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
                "instrument_name": "CRO_USDT",
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
                "instrument_name": "CRO_USDT",
                "side": buySell,
                "type": "STOP_LOSS",
                "trigger_price": price,
                "quantity": rCoins
            },
            "nonce": int(time.time() * 1000)
        }
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
                "instrument_name": "CRO_USDT"
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