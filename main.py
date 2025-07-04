import os
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram import Update

BOT_TOKEN = os.environ.get("BOT_TOKEN")
print("=== BOT_TOKEN is:", repr(BOT_TOKEN))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, I am your bot!")

def main():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN is missing!")
        exit(1)
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == "__main__":
    main()
