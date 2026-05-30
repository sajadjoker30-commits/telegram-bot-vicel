import os
import telebot
from flask import Flask, request

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

app = Flask(__name__)

@bot.message_handler(commands=["start"])
def start(m):
    bot.reply_to(m, "سلام! ربات روی Vercel فعال است.")

@app.route("/", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ""
    return "Forbidden", 403

@app.route("/", methods=["GET"])
def home():
    return "OK"
