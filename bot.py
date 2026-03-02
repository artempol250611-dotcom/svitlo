import os
import json
import re
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data.json"

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return

    lines = text.strip().split("\n")
    data = {}

    for line in lines:
        parts = line.strip().split()
        if len(parts) < 2:
            continue
        queue = parts[0]
        periods = parts[1:]
        for period in periods:
            match = re.match(r"(\d{2}:\d{2})-(\d{2}:\d{2})", period)
            if match:
                start, end = match.groups()
                data.setdefault(queue, [])
                data[queue].append({"start": start, "end": end})

    save_data(data)
    await update.message.reply_text("✅ Всі періоди відключень оновлено!")

async def run_bot():
    app_bot = ApplicationBuilder().token(TOKEN).build()
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app_bot.run_polling()

async def main():
    await asyncio.gather(run_flask(), run_bot())

if __name__ == "__main__":
    asyncio.run(main())