from flask import Flask, request, jsonify
import yfinance as yf
import requests
import time

app = Flask(__name__)

# кэш для криптовалют
crypto_cache = {}
CACHE_TTL = 60  # 1 минута

@app.route("/")
def home():
    return "Portfolio Server is running!"

@app.route("/stock")
def get_stock():
    symbol = request.args.get("symbol", "").upper()
    if not symbol:
        return jsonify({"error": "No symbol provided"}), 400

    try:
        ticker = yf.Ticker(symbol)
        price = ticker.fast_info.get("last_price")

        if price is None:
            return jsonify({"error": f"No data for {symbol}"})
        return jsonify({"price": price})
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/crypto")
def get_crypto():
    symbol = request.args.get("symbol", "").lower()
    if not symbol:
        return jsonify({"error": "No symbol provided"}), 400

    now = time.time()
    if symbol in crypto_cache and now - crypto_cache[symbol]["time"] < CACHE_TTL:
        return jsonify({"price": crypto_cache[symbol]["price"]})

    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        r = requests.get(url, timeout=10)
        data = r.json()

        if symbol not in data or "usd" not in data[symbol]:
            return jsonify({"error": f"No price for {symbol}"})

        price = data[symbol]["usd"]
        crypto_cache[symbol] = {"price": price, "time": now}
        return jsonify({"price": price})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
