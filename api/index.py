import os
import telebot
from flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in environment variables")

bot = telebot.TeleBot(TOKEN)

MAIN_CHANNEL = "@pouforce"
SOURCE_CHANNEL = "@uploderrrrrr"

app = Flask(__name__)

def check_membership(user_id: int) -> bool:
    try:
        member = bot.get_chat_member(MAIN_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        # برای دیباگ در لاگ‌های Vercel
        print("check_membership error:", repr(e))
        return False

@app.route("/", methods=["GET"])
def health():
    return "OK"

@app.route("/", methods=["POST"])
def webhook():
    try:
        if request.headers.get("content-type") == "application/json":
            update = telebot.types.Update.de_json(
                request.get_data().decode("utf-8")
            )
            bot.process_new_updates([update])
            return "OK"
        return "Unsupported Media Type", 415
    except Exception as e:
        print("webhook error:", repr(e))
        return "ERR", 500

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    parts = message.text.split(maxsplit=1)
    code = parts[1].strip() if len(parts) > 1 else None

    if not check_membership(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton("عضویت در کانال", url="https://t.me/pouforce")
        )
        bot.send_message(
            user_id,
            "❌ برای دریافت ویدئو ابتدا باید عضو کانال شوید.\n\nبعد از عضویت دوباره روی لینک دانلود بزنید.",
            reply_markup=markup
        )
        return

    if not code:
        bot.send_message(
            user_id,
            "سلام\nبرای دریافت ویدئو، روی لینک دانلودی که زیر پست کانال گذاشته‌ای کلیک کن."
        )
        return

    try:
        msg_id = int(code)
    except ValueError:
        bot.send_message(user_id, "❌ لینک نامعتبر است.")
        return

    try:
        bot.copy_message(
            chat_id=user_id,
            from_chat_id=SOURCE_CHANNEL,
            message_id=msg_id
        )
    except Exception as e:
        print("copy_message error:", repr(e))
        bot.send_message(
            user_id,
            "❌ ارسال ویدئو انجام نشد.\n\n"
            "بررسی کن:\n"
            "1) ربات در کانال @uploderrrrrr ادمین باشد\n"
            "2) message_id درست باشد\n"
            "3) ویدئو واقعاً در همان کانال موجود باشد"
        )
