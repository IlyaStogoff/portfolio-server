from flask import Flask, request, jsonify
from pycoingecko import CoinGeckoAPI
import requests
import time

app = Flask(__name__)
cg = CoinGeckoAPI()

# Кэш, чтобы не перегружать API
cache = {}
CACHE_TTL = 60  # 1 минута

def get_cached(key):
    if key in cache:
        value, ts = cache[key]
        if time.time() - ts < CACHE_TTL:
            return value
    return None

def set_cache(key, value):
    cache[key] = (value, time.time())


# ---------- КРИПТА ----------
@app.route("/crypto")
def crypto_price():
    symbol = request.args.get("symbol", "").lower()
    if not symbol:
        return jsonify({"error": "No symbol provided"}), 400

    cached = get_cached(f"crypto:{symbol}")
    if cached:
        return jsonify(cached)

    try:
        data = cg.get_price(ids=symbol, vs_currencies="usd")
        if symbol not in data:
            return jsonify({"error": f"No price for {symbol}"}), 404
        price = data[symbol]["usd"]

        result = {"price": float(price)}
        set_cache(f"crypto:{symbol}", result)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------- АКЦИИ ----------
@app.route("/stock")
def stock_price():
    symbol = request.args.get("symbol", "").upper()
    if not symbol:
        return jsonify({"error": "No symbol provided"}), 400

    cached = get_cached(f"stock:{symbol}")
    if cached:
        return jsonify(cached)

    try:
        url = f"https://query1.finance.yahoo.com/v7/finance/quote?symbols={symbol}"
        res = requests.get(url, timeout=5)
        data = res.json()

        result_data = data.get("quoteResponse", {}).get("result", [])
        if not result_data:
            return jsonify({"error": f"No data for {symbol}"}), 404

        price = result_data[0].get("regularMarketPrice")
        if not price:
            return jsonify({"error": f"No price for {symbol}"}), 404

        result = {"price": float(price)}
        set_cache(f"stock:{symbol}", result)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return "Portfolio API is running!"
