from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, ApplicationBuilder, CallbackQueryHandler, CommandHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
import os
import nest_asyncio
import asyncio
import requests

# إعداد Flask
app = Flask(__name__)

# --------- الحالة ---------
CHOOSING, TYPING_CONFESSION, AFTER_CONFESSION, CHOOSING_EXERCISE, TYPING_EXERCISE = range(5)
confessions_storage = []

# رابط Google Sheet API
GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbyMmr-a_dDJtbGm3ZZ3x1yDPi3arGghpU9jLh1ZqYe8Pnbj4CTxKtPY3rZp9MaYOoCP1w/exec"

# --------- الردود ---------
WELCOME_TEXT = """
🖤 مرحبًا في بلاك دفتر...
"""

MAIN_MENU_KEYBOARD = [
    [InlineKeyboardButton("دفترها الأسود", callback_data='black_book')],
    [InlineKeyboardButton("اعتراف", callback_data='confess')],
    [InlineKeyboardButton("التمارين", callback_data='exercises')],
    [InlineKeyboardButton("المكتبة", callback_data='library')],
]

BACK_TO_MENU = InlineKeyboardButton("⬅️ العودة إلى القائمة الرئيسية", callback_data='main_menu')

BLACK_BOOK_TEXT = """🖤 دفترها الأسود ليس مجرد دفتر..."""

CONFESSION_PROMPT = """🖤 لا أحد سيعرفكِ هنا… فقط اكتبي."""

POST_CONFESSION_TEXT = "🖤 كلماتكِ وصلت..."

POST_CONFESSION_KEYBOARD = [
    [InlineKeyboardButton("نعم، أرغب بتمرين", callback_data='yes_exercise')],
    [InlineKeyboardButton("لا، أعِدني إلى الصفحة الرئيسية", callback_data='main_menu')],
]

EXERCISES_LIST_TEXT = "🩻 اختاري التمرين المناسب لوجعكِ:"

EXERCISES_KEYBOARD = [
    [InlineKeyboardButton("🎀 طفولة تحتاج علاجًا", callback_data='exercise_childhood')],
    [InlineKeyboardButton("💞 جراح العلاقات", callback_data='exercise_relationships')],
    [InlineKeyboardButton("⚔️ معارك داخلية", callback_data='exercise_war')],
    [BACK_TO_MENU],
]

EXERCISE_INSTRUCTIONS = {
    'exercise_childhood': "🎀 تمرين الطفولة...",
    'exercise_relationships': "💞 تمرين العلاقات...",
    'exercise_war': "⚔️ تمرين الحرب الداخلية...",
}

EXERCISE_END_TEXT = "🖤 التمرين انتهى... تنفّسي."

LIBRARY_TEXT = """📘 مكتبة بلاك دفتر..."""

# إرسال إلى Google Sheets
async def send_to_sheet(entry_type, content, source="Telegram Bot"):
    try:
        requests.post(GOOGLE_SHEET_URL, json={
            "type": entry_type,
            "content": content,
            "source": source
        })
    except Exception as e:
        print("Google Sheet Error:", e)

# --------- HANDLERS ---------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(WELCOME_TEXT, reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD))
    return CHOOSING

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(WELCOME_TEXT, reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD))
    return CHOOSING

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'main_menu':
        return await main_menu(update, context)
    elif data == 'black_book':
        await query.edit_message_text(BLACK_BOOK_TEXT, reply_markup=InlineKeyboardMarkup([[BACK_TO_MENU]]))
        return CHOOSING
    elif data == 'confess':
        await query.edit_message_text(CONFESSION_PROMPT)
        return TYPING_CONFESSION
    elif data == 'exercises' or data == 'yes_exercise':
        await query.edit_message_text(EXERCISES_LIST_TEXT, reply_markup=InlineKeyboardMarkup(EXERCISES_KEYBOARD))
        return CHOOSING_EXERCISE
    elif data in EXERCISE_INSTRUCTIONS:
        await query.edit_message_text(EXERCISE_INSTRUCTIONS[data], reply_markup=InlineKeyboardMarkup([[BACK_TO_MENU]]), parse_mode='Markdown')
        return TYPING_EXERCISE if data != 'exercise_war' else CHOOSING
    elif data == 'library':
        await query.edit_message_text(LIBRARY_TEXT, reply_markup=InlineKeyboardMarkup([[BACK_TO_MENU]]), parse_mode='Markdown')
        return CHOOSING

async def confession_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text:
        confessions_storage.append(text)
        await send_to_sheet("اعتراف", text)
        await update.message.reply_text(POST_CONFESSION_TEXT, reply_markup=InlineKeyboardMarkup(POST_CONFESSION_KEYBOARD))
        return AFTER_CONFESSION
    return TYPING_CONFESSION

async def exercise_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text:
        await send_to_sheet("تمرين", text)
        await update.message.reply_text(EXERCISE_END_TEXT, reply_markup=InlineKeyboardMarkup([[BACK_TO_MENU]]), parse_mode='Markdown')
        return CHOOSING
    await update.message.reply_text("📩 اكتبي شيئًا ولو قصيرًا...")
    return TYPING_EXERCISE

# --------- TELEGRAM SETUP ---------
TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = "https://black-daftar-bot.onrender.com"

@app.post('/')
async def webhook():
    await telegram_app.update_queue.put(Update.de_json(request.get_json(force=True), telegram_app.bot))
    return "ok"

async def setup_bot():
    global telegram_app
    telegram_app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [CallbackQueryHandler(button_handler)],
            TYPING_CONFESSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, confession_received)],
            AFTER_CONFESSION: [CallbackQueryHandler(button_handler)],
            CHOOSING_EXERCISE: [CallbackQueryHandler(button_handler)],
            TYPING_EXERCISE: [MessageHandler(filters.TEXT & ~filters.COMMAND, exercise_response)],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    telegram_app.add_handler(conv_handler)
    await telegram_app.bot.set_webhook(url=WEBHOOK_URL)

# --------- START APP ---------
if __name__ == '__main__':
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(setup_bot())
    app.run(host='0.0.0.0', port=10000)

