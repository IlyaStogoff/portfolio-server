from flask import Flask, request, jsonify
import yfinance as yf
import requests

app = Flask(__name__)

# === КРИПТО ===
@app.route("/crypto")
def crypto_price():
    symbol = request.args.get("symbol", "").lower()
    if not symbol:
        return jsonify({"error": "No symbol provided"}), 400

    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()

        if symbol in data and "usd" in data[symbol]:
            return jsonify({"price": data[symbol]["usd"]})
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

    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")

        # если пусто — пробуем с .US
        if hist.empty:
            ticker = yf.Ticker(symbol + ".US")
            hist = ticker.history(period="1d")

        if hist.empty:
            return jsonify({"error": f"No data for {symbol}"}), 404

        price = hist["Close"].iloc[-1]
        return jsonify({"price": float(price)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return "Portfolio API is running!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
