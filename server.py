from flask import Flask, request, jsonify
import yfinance as yf
from pycoingecko import CoinGeckoAPI
import time

app = Flask(__name__)
cg = CoinGeckoAPI()

# простое кеширование
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


# ------------------ КРИПТА ------------------
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


# ------------------ АКЦИИ ------------------
@app.route("/stock")
def stock_price():
    symbol = request.args.get("symbol", "").upper()
    if not symbol:
        return jsonify({"error": "No symbol provided"}), 400

    cached = get_cached(f"stock:{symbol}")
    if cached:
        return jsonify(cached)

    try:
        ticker = yf.Ticker(symbol)

        price = None
        hist = ticker.history(period="1d")
        if not hist.empty:
            price = hist["Close"].iloc[-1]

        if not price:
            try:
                price = ticker.fast_info.last_price
            except Exception:
                pass

        if not price:
            return jsonify({"error": f"No data for {symbol}"}), 404

        result = {"price": float(price)}
        set_cache(f"stock:{symbol}", result)
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return "Portfolio API is running!"
