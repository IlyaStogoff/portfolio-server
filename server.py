from flask import Flask, request, jsonify
import yfinance as yf
import requests

app = Flask(__name__)

# === РОУТ ДЛЯ АКЦИЙ ===
@app.route("/stock")
def stock_price():
    symbol = request.args.get("symbol", "").upper()
    try:
        if not symbol:
            return jsonify({"error": "No symbol provided"}), 400

        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")

        if hist.empty:
            return jsonify({"error": f"No data for {symbol}"}), 404

        price = hist["Close"].iloc[-1]
        return jsonify({"price": float(price)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# === РОУТ ДЛЯ КРИПТЫ ===
@app.route("/crypto")
def crypto_price():
    symbol = request.args.get("symbol", "").lower()
    try:
        if not symbol:
            return jsonify({"error": "No symbol provided"}), 400

        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        res = requests.get(url, timeout=10)
        data = res.json()

        if symbol in data and "usd" in data[symbol]:
            return jsonify({"price": data[symbol]["usd"]})
        else:
            return jsonify({"error": f"No price for {symbol}"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# === ТЕСТОВАЯ ГЛАВНАЯ СТРАНИЦА ===
@app.route("/")
def home():
    return "Portfolio API is running 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
