// main.js
import { Telegraf, Markup } from 'telegraf';
import express from 'express';
import fetch from 'node-fetch';
import dotenv from 'dotenv';
dotenv.config();

const bot = new Telegraf(process.env.BOT_TOKEN);

// -------- KEEP ALIVE --------
const app = express();
app.get('/', (_req, res) => res.send('✅ البوت يعمل الآن…'));
app.listen(8080, () => console.log('✅ السيرفر يعمل على المنفذ 8080'));

// -------- BOT STATES --------
const STATE = {
  CHOOSING: 'CHOOSING',
  CONFESSION: 'CONFESSION',
  EXERCISE: 'EXERCISE'
};

const confessionsStorage = [];
const GOOGLE_SHEET_URL = "https://script.google.com/macros/s/AKfycbyMmr-a_dDJtbGm3ZZ3x1yDPi3arGghpU9jLh1ZqYe8Pnbj4CTxKtPY3rZp9MaYOoCP1w/exec";

const userStates = new Map();

async function sendToSheet(entryType, content, source = 'Telegram Bot') {
  try {
    await fetch(GOOGLE_SHEET_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type: entryType, content, source })
    });
  } catch (e) {
    console.error("Google Sheet Error:", e);
  }
}

// -------- TEXT CONTENT --------
const TEXT = {
  welcome: `🖤 مرحبًا في بلاك دفتر
البوت الرسمي لقناة دفترها الأسود…

لا حاجة لشرح ما لا يُفهم.
هنا نُرسل ما لم يُقال، ونطلب ما لم نجرؤ عليه.
🖤 في هذا المكان، لا أسماء ولا تواريخ… فقط نساء يُخرجن كلمات دفنتها الحروب، أو الحب، أو الخوف.

✦ اختاري ما ترغبين به من هذه المساحة الآن:`,

  blackBook: `🖤 دفترها الأسود ليس مجرد دفتر… إنه ركن صغير وملجأ حميم لأصوات لم يُسمح لها أن تبكي.

نكتب هنا عن نساء لم يُنقذهن أحد، عشن الطفولة وكأنها تهمة، والحب جرح.`,

  confessionPrompt: `🖤 لا أحد سيعرفكِ هنا… اكتبي كما لو أنكِ تهمسين لقلبكِ، لا أحد سيحكم، لا أحد سيقاطع.

📩 حين تنتهين، فقط أرسلي النص.`,

  postConfession: `🖤 كلماتكِ وصلت، وسنحتفظ بها كما تُحفظ الندبة…

هل ترغبين في تمرين بعد هذا الاعتراف؟`,

  exercisesList: `🩻 اختاري التمرين الذي يناسب وجعكِ الآن:`,

  exerciseEnd: `🖤 التمرين انتهى… لكن ما بداخلكِ لم ينتهِ، فقط بدأ يتنفّس.

ضعي يدكِ على صدرك، وقولي لنفسكِ:
"أنا أكتب كي أتنفس."`,

  library: `📘 مكتبة بلاك دفتر
منتجات علاجية كُتبت من الجرح… لا للقراءة، بل للنجاة.

📖 أشباح الذاكرة لا تموت
🖇️ https://tinyurl.com/goastmmry

🔪 دفترها الأسود – سكين أبي
🖇️ https://tinyurl.com/fatherscar`
};

const KEYBOARDS = {
  main: Markup.inlineKeyboard([
    [Markup.button.callback("دفترها الأسود", 'black_book')],
    [Markup.button.callback("اعتراف", 'confess')],
    [Markup.button.callback("التمارين", 'exercises')],
    [Markup.button.callback("المكتبة", 'library')],
  ]),
  back: Markup.inlineKeyboard([
    [Markup.button.callback("⬅️ العودة إلى القائمة الرئيسية", 'main')]
  ]),
  postConfession: Markup.inlineKeyboard([
    [Markup.button.callback("نعم، أرغب بتمرين", 'exercises')],
    [Markup.button.callback("لا، أعِدني إلى الصفحة الرئيسية", 'main')],
  ]),
  exercises: Markup.inlineKeyboard([
    [Markup.button.callback("🎀 طفولة تحتاج علاجًا", 'exercise_childhood')],
    [Markup.button.callback("💞 جراح العلاقات", 'exercise_relationships')],
    [Markup.button.callback("⚔️ معارك داخلية", 'exercise_war')],
    [Markup.button.callback("⬅️ العودة إلى القائمة الرئيسية", 'main')]
  ])
};

const EXERCISE_INSTRUCTIONS = {
  exercise_childhood: `🎀 ** تمرين الطفولة ** \n\n🕊️ تخيّلي طفلتكِ ذات السبع سنوات…\n- شيء تتمنين أن يُقال لكِ\n- شيء تريدين مسامحتها عليه\n- كلمة تشجيع واحدة... **من قلبكِ لقلبها**`,
  exercise_relationships: `💞 ** تمرين العلاقات **\n\n💔 ما الذي ترينه في مرآة الحب؟\nاكتبي انعكاسًا واحدًا ترغبين في تغييره… ليس فيهم، بل فيكِ.`,
  exercise_war: `⚔️ ** تمرين الحرب الداخلية **\n\n🏚️ اكتبي كل معاركك… ثم مزقي الورقة ببطء، كأنكِ تمزّقين الخوف.`
};

// -------- BOT LOGIC --------
bot.start((ctx) => {
  userStates.set(ctx.from.id, STATE.CHOOSING);
  return ctx.reply(TEXT.welcome, KEYBOARDS.main);
});

bot.action('main', (ctx) => {
  userStates.set(ctx.from.id, STATE.CHOOSING);
  return ctx.editMessageText(TEXT.welcome, KEYBOARDS.main);
});

bot.action('black_book', (ctx) => ctx.editMessageText(TEXT.blackBook, KEYBOARDS.back));

bot.action('confess', (ctx) => {
  userStates.set(ctx.from.id, STATE.CONFESSION);
  return ctx.editMessageText(TEXT.confessionPrompt);
});

bot.action('exercises', (ctx) => {
  userStates.set(ctx.from.id, STATE.EXERCISE);
  return ctx.editMessageText(TEXT.exercisesList, KEYBOARDS.exercises);
});

bot.action('library', (ctx) => ctx.editMessageText(TEXT.library, KEYBOARDS.back));

bot.action(/exercise_.+/, (ctx) => {
  const id = ctx.callbackQuery.data;
  return ctx.editMessageText(EXERCISE_INSTRUCTIONS[id], {
    parse_mode: 'Markdown',
    ...KEYBOARDS.back
  });
});

bot.on('text', async (ctx) => {
  const state = userStates.get(ctx.from.id);
  const text = ctx.message.text.trim();

  if (state === STATE.CONFESSION) {
    confessionsStorage.push(text);
    await sendToSheet("اعتراف", text);
    userStates.set(ctx.from.id, STATE.CHOOSING);
    return ctx.reply(TEXT.postConfession, KEYBOARDS.postConfession);
  }

  if (state === STATE.EXERCISE) {
    await sendToSheet("تمرين", text);
    userStates.set(ctx.from.id, STATE.CHOOSING);
    return ctx.reply(TEXT.exerciseEnd, KEYBOARDS.back);
  }
});

// -------- RUN BOT --------
bot.launch()
  .then(() => console.log('✅ البوت يعمل الآن...'))
  .catch(console.error);

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
