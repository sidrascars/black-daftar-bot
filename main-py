from flask import Flask, request
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, ContextTypes, ConversationHandler,
    CallbackQueryHandler, MessageHandler, filters
)
import requests
import os
import nest_asyncio
import asyncio

# --- Flask App ---
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ البوت يعمل الآن…"

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), application.bot)
        asyncio.run(application.process_update(update))
        return 'ok'

# --- Keep alive on Render ---
def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=port))
    t.start()

# --- States ---
CHOOSING, TYPING_CONFESSION, AFTER_CONFESSION, CHOOSING_EXERCISE, TYPING_EXERCISE = range(5)

# --- Static texts and buttons (اختصري هنا لو أردتِ) ---
WELCOME_TEXT = "مرحبا"
MAIN_MENU_KEYBOARD = [[InlineKeyboardButton("ابدئي", callback_data='start')]]
BACK_TO_MENU = InlineKeyboardButton("⬅️ العودة", callback_data='main_menu')

# --- Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD))
    return CHOOSING

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(WELCOME_TEXT, reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD))
    return CHOOSING

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await main_menu(update, context)

# --- Setup Bot ---
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    print("❗ BOT_TOKEN غير موجود")
    exit()

application = Application.builder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        CHOOSING: [CallbackQueryHandler(button_handler)],
    },
    fallbacks=[CommandHandler('start', start)],
)

application.add_handler(conv_handler)

# --- Webhook setup ---
async def set_webhook():
    url = os.environ.get("RENDER_EXTERNAL_URL") or "https://black-daftar-bot.onrender.com"
    webhook_url = f"{url}/webhook"
    await application.bot.set_webhook(webhook_url)

# --- Main Execution ---
if __name__ == '__main__':
    nest_asyncio.apply()
    keep_alive()
    asyncio.run(set_webhook())
