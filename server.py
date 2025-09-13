from flask import Flask, request, jsonify
import yfinance as yf
import requests

app = Flask(__name__)

# === Маршрут для проверки ===
@app.route("/")
def home():
    return "Portfolio API is running!"

# === Получение цены акции через Yahoo Finance ===
@app.route("/stock")
def get_stock_price():
    symbol = request.args.get("symbol")
    if not symbol:
        return jsonify({"error": "No symbol provided"}), 400
    try:
        ticker = yf.Ticker(symbol)
        price = ticker.history(period="1d")["Close"].iloc[-1]
        return jsonify({"price": float(price)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# === Получение цены криптовалюты через CoinGecko ===
@app.route("/crypto")
def get_crypto_price():
    symbol = request.args.get("symbol", "").lower()
    if not symbol:
        return jsonify({"error": "No symbol provided"}), 400
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        res = requests.get(url)
        data = res.json()
        if symbol in data and "usd" in data[symbol]:
            return jsonify({"price": data[symbol]["usd"]})
        else:
            return jsonify({"price": 0})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
