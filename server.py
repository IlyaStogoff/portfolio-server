from flask import Flask, request
import requests, time

app = Flask(__name__)

# Кэш цен, чтобы не долбить API
cache = {}
TTL = 300  # 5 минут

@app.route("/crypto")
def crypto():
    symbol = request.args.get("symbol", "").lower()
    if not symbol:
        return "0", 400
    now = time.time()
    if symbol in cache and now - cache[symbol]['t'] < TTL:
        return str(cache[symbol]['p'])
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
    r = requests.get(url, timeout=10)
    data = r.json()
    price = data.get(symbol, {}).get("usd", 0)
    cache[symbol] = {'p': price, 't': now}
    return str(price)

@app.route("/")
def home():
    return "Crypto Price API работает 🚀"
