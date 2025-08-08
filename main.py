from flask import Flask, request, jsonify
from binance.client import Client
from binance.enums import *
import os

app = Flask(__name__)

# ⚠️ Configura tus API Keys en variables de entorno
API_KEY = os.getenv("BINANCE_API_KEY", "TU_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET", "TU_API_SECRET")

client = Client(API_KEY, API_SECRET)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()

        # Validar campos
        if not all(k in data for k in ("side", "symbol", "quantity")):
            return jsonify({"error": "Faltan datos en el JSON"}), 400

        side = data['side'].lower()
        symbol = data['symbol'].upper()
        quantity = float(data['quantity'])

        if quantity <= 0:
            return jsonify({"error": "Cantidad inválida"}), 400

        if side == "buy":
            order = client.order_market_buy(
                symbol=symbol,
                quantity=quantity
            )
        elif side == "sell":
            order = client.order_market_sell(
                symbol=symbol,
                quantity=quantity
            )
        else:
            return jsonify({"error": "Side inválido, usa 'buy' o 'sell'"}), 400

        return jsonify({"status": "success", "order": order})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return "✅ Bot de Binance Spot activo"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
