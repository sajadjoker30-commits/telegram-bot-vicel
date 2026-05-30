from flask import Flask, request
import telebot, os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    # اگر توکن نباشد، برنامه شروع نمی‌شود و لاگ runtime error می‌دهد
    raise RuntimeError("BOT_TOKEN is not set in Vercel environment variables")

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# -- اینجا را با منطق کامل Force Join و Send Message جایگزین کن --
# این فقط برای تست اتصال اولیه است
@bot.message_handler(commands=["start"])
def start(m):
    print(f"Received command: {m.text} from chat ID: {m.chat.id}")
    try:
        # سعی کن یک پیام ساده بفرستی
        bot.send_message(m.chat.id, "بات آنلاین است و در حال پردازش درخواست شما...")
        print(f"Sent initial message to chat ID: {m.chat.id}")
    except Exception as e:
        print(f"ERROR sending initial message to chat ID {m.chat.id}: {e}")
        # اگر ارسال اولیه هم خطا داد، اینجا مشخص می‌شود

@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "OK", 200

    # -- لاگ‌های اجباری برای تشخیص مشکل POST --
    print("WEBHOOK HIT")
    json_data = request.get_json(silent=True)
    print("JSON DATA:", json_data) # لاگ کردن اطلاعات خام JSON دریافتی

    if not json_data:
        print("ERROR: No JSON data received")
        return "Bad Request: No JSON", 400

    try:
        update = telebot.types.Update.de_json(json_data, bot)
        bot.process_new_updates([update])
        print("Successfully processed update")
        return "OK", 200
    except Exception as e:
        print(f"ERROR processing update: {e}")
        # اگر خطایی در پردازش آپدیت رخ دهد، اینجا لاگ می‌شود
        return "Internal Server Error", 500
