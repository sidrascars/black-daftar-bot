const { Telegraf } = require('telegraf');

// احصل على التوكن من متغير البيئة
const bot = new Telegraf(process.env.BOT_TOKEN);

// أمر /start
bot.start((ctx) => ctx.reply('مرحباً! أنا بوت تيليجرام بلغة Node.js 🚀'));

// أمر /help
bot.help((ctx) => ctx.reply('أرسل أي رسالة وسأرددها لك!'));

// بوت يكرر الرسائل
bot.on('text', (ctx) => ctx.reply(`قلت: ${ctx.message.text}`));

// تشغيل البوت
bot.launch();

// إغلاق آمن عند إيقاف السيرفر
process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
