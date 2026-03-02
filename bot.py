import os
import json
import threading
from datetime import datetime
from flask import Flask, render_template, jsonify
from telegram.ext import ApplicationBuilder, MessageHandler, filters

# --- КОНФИГУРАЦИЯ ---
TOKEN = "BOT_TOKEN"
DATA_FILE = "data.json"

app = Flask(__name__)

# --- ЛОГИКА РАБОТЫ С ДАННЫМИ ---
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"today": {}, "tomorrow": {}}
    except Exception as e:
        print(f"Ошибка чтения: {e}")
        return {"today": {}, "tomorrow": {}}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def current_status(periods):
    now = datetime.now().strftime("%H:%M")
    for p in periods:
        if p["start"] <= now <= p["end"]:
            return "off"
    return "on"

def parse_block(lines):
    result = {}
    for line in lines:
        parts = line.split()
        if len(parts) < 2: continue
        queue = parts[0]
        periods = []
        for time_range in parts[1:]:
            try:
                start, end = time_range.split("-")
                periods.append({"start": start, "end": end})
            except: continue
        result[queue] = periods
    return result

# --- ОБРАБОТЧИК ТЕЛЕГРАМ ---
async def handle_tg_message(update, context):
    text = update.message.text.lower()
    data = load_data()

    blocks = text.split("\n\n")
    for block in blocks:
        lines = block.strip().split("\n")
        if not lines: continue
        header = lines[0]
        content = lines[1:]
        if "сегодня" in header:
            data["today"] = parse_block(content)
        elif "завтра" in header:
            data["tomorrow"] = parse_block(content)

    save_data(data)
    await update.message.reply_text("✅ Графік оновлено!")

# --- МАРШРУТЫ САЙТА (FLASK) ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def get_data():
    raw = load_data()
    result = {"today": {}, "tomorrow": {}}
    for tab in ["today", "tomorrow"]:
        for queue, periods in raw.get(tab, {}).items():
            status = current_status(periods) if tab == "today" else "on"
            result[tab][queue] = {"status": status, "periods": periods}
    return jsonify(result)

# --- ФУНКЦИЯ ЗАПУСКА БОТА ---
def run_bot():
    # Создаем приложение бота
    tg_app = ApplicationBuilder().token(TOKEN).build()
    tg_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_tg_message))
    print("BOT STARTED 🚀")
    tg_app.run_polling(close_loop=False)

# --- ЗАПУСК ВСЕГО ВМЕСТЕ ---
if __name__ == "__main__":
    # 1. Запускаем бота в отдельном потоке, чтобы он не мешал сайту
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # 2. Запускаем сайт Flask
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)