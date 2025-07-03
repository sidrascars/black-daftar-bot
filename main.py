from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    CommandHandler
)
import os
import nest_asyncio
import asyncio

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

application = ApplicationBuilder().token(BOT_TOKEN).build()

@app.route(f"/{BOT_TOKEN}", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    await application.process_update(update)
    return "ok"

@app.route('/')
def home():
    return "✅ البوت يعمل الآن…"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🖤 مرحبًا في بلاك دفتر. البوت يعمل عبر Webhook على Render.")

async def run():
    application.add_handler(CommandHandler("start", start))
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{BOT_TOKEN}")
    print("✅ Webhook تم تفعيله.")

if __name__ == "__main__":
    nest_asyncio.apply()
    asyncio.run(run())
    app.run(host="0.0.0.0", port=10000)
