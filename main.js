const { Telegraf, Markup } = require('telegraf');
const axios = require('axios');
const express = require('express');
const app = express();

// -------- إعداد Keep Alive --------
app.get('/', (req, res) => {
  res.send('✅ البوت يعمل الآن…');
});

app.listen(8080, () => {
  console.log('🌐 السيرفر يعمل على المنفذ 8080');
});

// -------- إعداد التوكن والبوت --------
const BOT_TOKEN = process.env.BOT_TOKEN;
if (!BOT_TOKEN) throw new Error('❗ BOT_TOKEN غير موجود في environment variables');

const bot = new Telegraf(BOT_TOKEN);

// -------- البيانات --------
const confessions_storage = [];
const GOOGLE_SHEET_URL = 'https://script.google.com/macros/s/AKfycbyMmr-a_dDJtbGm3ZZ3x1yDPi3arGghpU9jLh1ZqYe8Pnbj4CTxKtPY3rZp9MaYOoCP1w/exec';

const sendToSheet = async (type, content, source = 'Telegram Bot') => {
  try {
    await axios.post(GOOGLE_SHEET_URL, { type, content, source });
  } catch (e) {
    console.error('Google Sheet Error:', e);
  }
};

const texts = {
  welcome: `🖤 مرحبًا في بلاك دفتر...\n✦ اختاري ما ترغبين به من هذه المساحة الآن:`,
  black_book: `🖤 دفترها الأسود ليس مجرد دفتر…\nإنه ركن صغير وملجأ حميم لأصوات لم يُسمح لها أن تبكي.`,
  confession_prompt: `🖤 لا أحد سيعرفكِ هنا…\n📩 حين تنتهين، فقط أرسلي النص.`,
  after_confession: `🖤 كلماتكِ وصلت...\nهل ترغبين في تمرين بعد هذا الاعتراف؟`,
  exercises_intro: `🩻 اختاري التمرين الذي يناسب وجعكِ الآن:`,
  exercise_end: `🖤 التمرين انتهى…\n"أنا أكتب كي أتنفس."`,
  library: `📘 مكتبة بلاك دفتر\n📖 أشباح الذاكرة لا تموت: https://tinyurl.com/goastmmry\n🔪 دفترها الأسود – سكين أبي: https://tinyurl.com/fatherscar`
};

const exercises = {
  exercise_childhood: `🎀 ** تمرين الطفولة **\n🕊️ تخيّلي طفلتكِ...`,
  exercise_relationships: `💞 ** تمرين العلاقات **\n💔 ما الذي ترينه في مرآة الحب؟`,
  exercise_war: `⚔️ ** تمرين الحرب الداخلية **\n🏚️ اكتبي كل معاركك...`
};

const mainMenu = Markup.inlineKeyboard([
  [Markup.button.callback('دفترها الأسود', 'black_book')],
  [Markup.button.callback('اعتراف', 'confess')],
  [Markup.button.callback('التمارين', 'exercises')],
  [Markup.button.callback('المكتبة', 'library')]
]);

const backToMenu = Markup.inlineKeyboard([
  [Markup.button.callback('⬅️ العودة إلى القائمة الرئيسية', 'main_menu')]
]);

const postConfessionKeyboard = Markup.inlineKeyboard([
  [Markup.button.callback('نعم، أرغب بتمرين', 'yes_exercise')],
  [Markup.button.callback('لا، أعِدني إلى الصفحة الرئيسية', 'main_menu')]
]);

const exercisesMenu = Markup.inlineKeyboard([
  [Markup.button.callback('🎀 طفولة تحتاج علاجًا', 'exercise_childhood')],
  [Markup.button.callback('💞 جراح العلاقات', 'exercise_relationships')],
  [Markup.button.callback('⚔️ معارك داخلية', 'exercise_war')],
  [Markup.button.callback('⬅️ العودة إلى القائمة الرئيسية', 'main_menu')]
]);

// -------- Handlers --------
bot.start((ctx) => ctx.reply(texts.welcome, mainMenu));

bot.action('main_menu', (ctx) => ctx.editMessageText(texts.welcome, mainMenu));

bot.action('black_book', (ctx) => ctx.editMessageText(texts.black_book, backToMenu));

bot.action('confess', (ctx) => {
  ctx.editMessageText(texts.confession_prompt);
  bot.once('text', async (ctx2) => {
    const confession = ctx2.message.text;
    confessions_storage.push(confession);
    await sendToSheet('اعتراف', confession);
    await ctx2.reply(texts.after_confession, postConfessionKeyboard);
  });
});

bot.action(['yes_exercise', 'exercises'], (ctx) => {
  ctx.editMessageText(texts.exercises_intro, exercisesMenu);
});

bot.action(['exercise_childhood', 'exercise_relationships', 'exercise_war'], (ctx) => {
  const content = exercises[ctx.match[0]];
  ctx.editMessageText(content, backToMenu);
  bot.once('text', async (ctx2) => {
    const answer = ctx2.message.text;
    await sendToSheet('تمرين', answer);
    await ctx2.reply(texts.exercise_end, backToMenu);
  });
});

bot.action('library', (ctx) => ctx.editMessageText(texts.library, backToMenu));

// -------- إطلاق البوت --------
bot.launch();

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));

console.log('🤖 البوت قيد التشغيل...');
