import os
import asyncio
from flask import Flask, render_template, jsonify
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def data():
    # Зчитуємо дані з JSON
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception as e:
        raw = {}

    result = {}
    now = datetime.now().strftime("%H:%M")
    for queue, periods in raw.items():
        status = "on"
        for p in periods:
            if p["start"] <= now <= p["end"]:
                status = "off"
                break
        result[queue] = status
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)