from flask import Flask, request, jsonify
import json
import os
from binance.client import Client
from binance.enums import *

# ⚠️ WPIBYswfCdoxElwnMvBmBNvy0Rkatw0ukFR7QbFrDjnDxOO6sKDqKYCmDROshmxz (usa testnet=True para pruebas)
API_KEY = os.getenv("BINANCE_API_KEY", "TU_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET", "TU_API_SECRET")
client = Client(API_KEY, API_SECRET, testnet=True)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = json.loads(request.data)

        action = data.get("action")
        symbol = data.get("symbol")
        qty_pct = float(data.get("qty_pct", 0))
        price = float(data.get("price", 0))

        # Calcular cantidad a comprar/vender
        balance = float(client.futures_account_balance()[0]['balance'])
        qty = round((balance * (qty_pct / 100)) / price, 3)

        if action == "BUY":
            order = client.futures_create_order(
                symbol=symbol,
                side=SIDE_BUY,
                type=ORDER_TYPE_MARKET,
                quantity=qty
            )
            print("🚀 Long abierto", order)

        elif action == "SELL":
            order = client.futures_create_order(
                symbol=symbol,
                side=SIDE_SELL,
                type=ORDER_TYPE_MARKET,
                quantity=qty
            )
            print("🔻 Short abierto", order)

        elif action == "CLOSE":
            side_close = SIDE_SELL if data.get("side") == "LONG" else SIDE_BUY
            order = client.futures_create_order(
                symbol=symbol,
                side=side_close,
                type=ORDER_TYPE_MARKET,
                quantity=qty
            )
            print("✅ Posición cerrada", order)

        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
