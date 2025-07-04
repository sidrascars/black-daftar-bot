import os
print("BOT_TOKEN:", os.environ.get("BOT_TOKEN"))
print("BOT_URL:", os.environ.get("BOT_URL"))import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import nest_asyncio

nest_asyncio.apply()

# استدعاء التوكن والرابط من متغيرات البيئة
BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_URL = os.environ.get("BOT_URL")

if not BOT_TOKEN or not BOT_URL:
    print("❗ BOT_TOKEN أو BOT_URL غير موجودين")
    exit()

bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()


# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحبًا بك في دفتر الاعترافات 🖤")


application.add_handler(CommandHandler("start", start))


# إعداد webhook على تيليغرام
@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "ok"


# ربط البوت بالرابط الخاص
@app.route('/')
def index():
    bot.set_webhook(url=f"{BOT_URL}/webhook")
    return "✅ Webhook set successfully"


if __name__ == '__main__':
    app.run(port=10000)
