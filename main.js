const express = require("express");
const { Telegraf } = require("telegraf");
require("dotenv").config();

const bot = new Telegraf(process.env.BOT_TOKEN);
const app = express();

bot.start((ctx) => ctx.reply("مرحبًا بكِ في بلاك دفتر!"));

bot.telegram.setWebhook(process.env.BOT_URL + "/bot" + process.env.BOT_TOKEN);
app.use(bot.webhookCallback("/bot" + process.env.BOT_TOKEN));

app.get("/", (req, res) => {
  res.send("بوت بلاك دفتر يعمل ✅");
});

app.listen(process.env.PORT || 3000, () => {
  console.log("Bot server is running");
});
