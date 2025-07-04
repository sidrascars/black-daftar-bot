import os
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from flask import Flask

app = Flask(__name__)
TOKEN = os.environ.get('TOKEN')

@app.route('/')
def home():
    return "Bot is alive!"

def start(update: Update, context: CallbackContext):
    update.message.reply_text('✅ البوت يعمل! أرسل أي رسالة')

def echo(update: Update, context: CallbackContext):
    update.message.reply_text(f'📢: {update.message.text}')

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    updater.start_polling()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

if __name__ == '__main__':
    main()
