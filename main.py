from flask import Flask
from threading import Thread
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler,
    CallbackQueryHandler, MessageHandler, filters
)
import requests
import os
import asyncio
import nest_asyncio

# --------- KEEP ALIVE SETUP ---------
app = Flask('')

@app.route('/')
def home():
    return "✅ البوت يعمل الآن…"

def keep_alive():
    t = Thread(target=lambda: app.run(host='0.0.0.0', port=8080))
    t.start()

# --------- BOT STATES ---------
CHOOSING, TYPING_CONFESSION, AFTER_CONFESSION, CHOOSING_EXERCISE, TYPING_EXERCISE = range(5)

confessions_storage = []

GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbyMmr-a_dDJtbGm3ZZ3x1yDPi3arGghpU9jLh1ZqYe8Pnbj4CTxKtPY3rZp9MaYOoCP1w/exec"

async def send_to_sheet(entry_type, content, source="Telegram Bot"):
    try:
        requests.post(GOOGLE_SHEET_URL, json={
            "type": entry_type,
            "content": content,
            "source": source
        })
    except Exception as e:
        print("Google Sheet Error:", e)

# --------- TEXT CONTENT ---------
WELCOME_TEXT = """
🖤 مرحبًا في بلاك دفتر
البوت الرسمي لقناة دفترها الأسود…

لا حاجة لشرح ما لا يُفهم.
هنا نُرسل ما لم يُقال، ونطلب ما لم نجرؤ عليه.
🖤 في هذا المكان، لا أسماء ولا تواريخ…
فقط نساء يُخرجن من صدورهن كلمات دفنتها الحروب، أو الحب، أو الخوف.

✦ اختاري ما ترغبين به من هذه المساحة الآن:
"""

MAIN_MENU_KEYBOARD = [
    [InlineKeyboardButton("دفترها الأسود", callback_data='black_book')],
    [InlineKeyboardButton("اعتراف", callback_data='confess')],
    [InlineKeyboardButton("التمارين", callback_data='exercises')],
    [InlineKeyboardButton("المكتبة", callback_data='library')],
]

BACK_TO_MENU = InlineKeyboardButton("⬅️ العودة إلى القائمة الرئيسية", callback_data='main_menu')

BLACK_BOOK_TEXT = """
🖤 دفترها الأسود ليس مجرد دفتر…
إنه مقبرة صغيرة لأصوات لم يُسمح لها أن تبكي.

نكتب هنا عن نساء لم يُنقذهن أحد،
عشن الطفولة وكأنها تهمة، والحب جرح.
"""

CONFESSION_PROMPT = """
🖤 لا أحد سيعرفكِ هنا…
🖤 اكتبي كما لو أنكِ تهمسين لقلبكِ،
لا أحد سيحكم، لا أحد سيقاطع، لا أحد سيطلب تفسيرًا.

📩 حين تنتهين، فقط أرسلي النص.
"""

POST_CONFESSION_TEXT = """
🖤 كلماتكِ وصلت، وسنحتفظ بها كما تُحفظ الندبة…

هل ترغبين في تمرين بعد هذا الاعتراف؟
"""

POST_CONFESSION_KEYBOARD = [
    [InlineKeyboardButton("نعم، أرغب بتمرين", callback_data='yes_exercise')],
    [InlineKeyboardButton("لا، أعِدني إلى الصفحة الرئيسية", callback_data='main_menu')],
]

EXERCISES_LIST_TEXT = """
🩻 اختاري التمرين الذي يناسب وجعكِ الآن:
"""

EXERCISES_KEYBOARD = [
    [InlineKeyboardButton("🎀 طفولة تحتاج علاجًا", callback_data='exercise_childhood')],
    [InlineKeyboardButton("💞 جراح العلاقات", callback_data='exercise_relationships')],
    [InlineKeyboardButton("⚔️ معارك داخلية", callback_data='exercise_war')],
    [BACK_TO_MENU],
]

EXERCISE_INSTRUCTIONS = {
    'exercise_childhood': """
🎀 ** تمرين الطفولة ** 

🕊️ تخيّلي طفلتكِ ذات السبع سنوات تقف أمامك…

اكتبي لها:
- شيء تتمنين أن يُقال لكِ وقتها  
- شيء تريدين مسامحتها عليه  
- كلمة تشجيع واحدة... **من قلبكِ لقلبها**
""",
    'exercise_relationships': """
💞 ** تمرين العلاقات ** 

💔 ما الذي ترينه في مرآة الحب؟ في مرآة الصداقة؟

اكتبي **انعكاسًا واحدًا** ترغبين في تغييره…  
ليس فيهم، بل فيكِ.
""",
    'exercise_war': """
⚔️ ** تمرين الحرب الداخلية **  

🏚️ اكتبي كل معاركك مع نفسك والآخرين…

ثم مزقي الورقة ببطء، كأنكِ تمزّقين الخوف نفسه.
""",
}

EXERCISE_END_TEXT = """
🖤 التمرين انتهى…  
لكن ما بداخلكِ لم ينتهِ، فقط بدأ يتنفّس.

ضعي يدكِ على صدرك،  
وقولي لنفسكِ:

"أنا أكتب كي أتنفس."
"""

LIBRARY_TEXT = """
📘 مكتبة بلاك دفتر  
منتجات علاجية كُتبت من الجرح… لا للقراءة، بل للنجاة.

📖 أشباح الذاكرة لا تموت  
🖇️ [قراءة الكتيّب](https://tinyurl.com/goastmmry)

🔪 دفترها الأسود – سكين أبي  
🖇️ [قراءة الكتيّب](https://tinyurl.com/fatherscar)
"""

# --------- BOT FUNCTIONS ---------

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
        if data == 'exercise_war':
            return CHOOSING
        else:
            return TYPING_EXERCISE

    elif data == 'library':
        await query.edit_message_text(LIBRARY_TEXT, reply_markup=InlineKeyboardMarkup([[BACK_TO_MENU]]), parse_mode='Markdown')
        return CHOOSING

async def confession_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text:
        confessions_storage.append(text)
        await send_to_sheet("اعتراف", text)
        await update.message.reply_text(
            POST_CONFESSION_TEXT,
            reply_markup=InlineKeyboardMarkup(POST_CONFESSION_KEYBOARD)
        )
        return AFTER_CONFESSION
    return TYPING_CONFESSION

async def exercise_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if text:
        await send_to_sheet("تمرين", text)
        await update.message.reply_text(
            EXERCISE_END_TEXT,
            reply_markup=InlineKeyboardMarkup([[BACK_TO_MENU]]),
            parse_mode='Markdown'
        )
        return CHOOSING
    await update.message.reply_text("📩 اكتبي شيئًا حتى ولو كان عبارة قصيرة…")
    return TYPING_EXERCISE

# --------- MAIN ---------

async def main():
    TOKEN = os.environ.get("BOT_TOKEN")
    if not TOKEN:
        print("❗ BOT_TOKEN غير موجود")
        return

    app = ApplicationBuilder().token(TOKEN).build()

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

    app.add_handler(conv_handler)

    print("✅ البوت يعمل الآن...")
    await app.run_polling()

if __name__ == '__main__':
    nest_asyncio.apply()
    keep_alive()
    asyncio.run(main())
from keep_alive import keep_alive
import nest_asyncio
import asyncio

if __name__ == '__main__':
    from keep_alive import keep_alive
    import nest_asyncio
    import asyncio
    from keep_alive import keep_alive

    if __name__ == '__main__':
        keep_alive()
        nest_asyncio.apply()
        asyncio.run(main())

