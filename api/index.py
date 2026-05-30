from flask import Flask, request
import telebot, os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in Vercel env vars")

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

@bot.message_handler(commands=['start'])
def start(m):
    bot.send_message(m.chat.id, "بات آنلاین است")

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "OK", 200

    # Telegram POST
    update = telebot.types.Update.de_json(request.get_json(force=True), bot)
    bot.process_new_updates([update])
    return "OK", 200
