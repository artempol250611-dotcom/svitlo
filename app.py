import os
import json
from datetime import datetime
from flask import Flask, render_template, jsonify

app = Flask(__name__)
DATA_FILE = "data.json"

def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"today": {}, "tomorrow": {}}
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return {"today": {}, "tomorrow": {}}

def current_status(periods):
    # Убедись, что время на сервере совпадает с твоим часовым поясом
    now = datetime.now().strftime("%H:%M")
    for p in periods:
        if p["start"] <= now <= p["end"]:
            return "off"
    return "on"

@app.route("/data")
def data():
    raw = load_data()
    result = {"today": {}, "tomorrow": {}}

    for tab in ["today", "tomorrow"]:
        for queue, periods in raw.get(tab, {}).items():
            # Для "сегодня" считаем статус, для "завтра" просто отдаем периоды
            status = current_status(periods) if tab == "today" else "on"
            result[tab][queue] = {"status": status, "periods": periods}
    return jsonify(result)

@app.route("/")
def index():
    return render_template("index.html")

# --- БЛОК ЗАПУСКА ДЛЯ RENDER ---
if __name__ == "__main__":
    # Render передает порт в переменную окружения PORT
    port = int(os.environ.get("PORT", 5000))
    # host='0.0.0.0' обязателен для доступа из интернета
    app.run(host='0.0.0.0', port=port, debug=False)