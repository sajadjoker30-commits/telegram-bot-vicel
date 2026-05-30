import os
import telebot
from flask import Flask, request

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# کانال عضویت اجباری
MAIN_CHANNEL = "@pouforce"

# کانال منبع ویدئوها
SOURCE_CHANNEL = "@uploderrrrrr"

app = Flask(__name__)

def check_membership(user_id: int) -> bool:
    try:
        member = bot.get_chat_member(MAIN_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

@app.route("/", methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ""
    return "Method Not Allowed", 405

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id

    # گرفتن message_id از deep link
    # مثال: /start 456
    parts = message.text.split(maxsplit=1)
    code = parts[1].strip() if len(parts) > 1 else None

    # بررسی عضویت اجباری
    if not check_membership(user_id):
        markup = telebot.types.InlineKeyboardMarkup()
        join_btn = telebot.types.InlineKeyboardButton(
            "عضویت در کانال",
            url="https://t.me/pouforce"
        )
        markup.add(join_btn)

        bot.send_message(
            user_id,
            "❌ برای دریافت ویدئو ابتدا باید عضو کانال شوید.\n\nبعد از عضویت دوباره روی لینک دانلود بزنید.",
            reply_markup=markup
        )
        return

    # اگر کاربر بدون لینک وارد بات شد
    if not code:
        bot.send_message(
            user_id,
            "سلام 👋\nبرای دریافت ویدئو، روی لینک دانلودی که زیر پست کانال گذاشته‌ای کلیک کن."
        )
        return

    # تبدیل code به message_id
    try:
        msg_id = int(code)
    except ValueError:
        bot.send_message(user_id, "❌ لینک نامعتبر است.")
        return

    # کپی پیام ویدئو از کانال منبع به کاربر
    try:
        bot.copy_message(
            chat_id=user_id,
            from_chat_id=SOURCE_CHANNEL,
            message_id=msg_id
        )
    except Exception:
        bot.send_message(
            user_id,
            "❌ ارسال ویدئو انجام نشد.\n\n"
            "بررسی کن:\n"
            "1) ربات در کانال @uploderrrrrr ادمین باشد\n"
            "2) message_id درست باشد\n"
            "3) ویدئو واقعاً در همان کانال موجود باشد"
        )

if __name__ == "__main__":
    app.run()
