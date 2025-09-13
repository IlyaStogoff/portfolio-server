from flask import Flask, request, jsonify
import yfinance as yf
import requests, time

app = Flask(__name__)

cache = {}  # простое кэширование {ключ: (время, данные)}
CACHE_TTL = 60  # 60 секунд


def get_cached(key):
    if key in cache:
        ts, data = cache[key]
        if time.time() - ts < CACHE_TTL:
            return data
    return None


def set_cache(key, data):
    cache[key] = (time.time(), data)


# === КРИПТО ===
@app.route("/crypto")
def crypto_price():
    symbol = request.args.get("symbol", "").lower()
    if not symbol:
        return jsonify({"error": "No symbol provided"}), 400

    cached = get_cached(f"crypto:{symbol}")
    if cached:
        return jsonify(cached)

    try:
        # 1) Попробуем через Yahoo (пример: BTC-USD)
        ticker = yf.Ticker(symbol.upper() + "-USD")
        price = ticker.fast_info.last_price
        if price:
            result = {"price": float(price)}
            set_cache(f"crypto:{symbol}", result)
            return jsonify(result)

        # 2) Если не нашли — идём в CoinGecko
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        if symbol in data and "usd" in data[symbol]:
            result = {"price": data[symbol]["usd"]}
            set_cache(f"crypto:{symbol}", result)
            return jsonify(result)
        else:
            return jsonify({"error": f"No price for {symbol}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# === АКЦИИ ===
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
        price = ticker.fast_info.last_price
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
