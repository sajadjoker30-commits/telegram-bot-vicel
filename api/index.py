from flask import Flask, request
import telebot, os

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in Vercel environment variables")

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# -- لاگ‌های اجباری برای تشخیص مشکل POST --
@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "OK", 200

    print("WEBHOOK HIT")
    json_data = request.get_json(silent=True)
    print("JSON DATA:", json_data)

    if not json_data:
        print("ERROR: No JSON data received")
        return "Bad Request: No JSON", 400

    try:
        # --- اصلاح شده ---
        update = telebot.types.Update.de_json(json_data)
        # ------------------
        bot.process_new_updates([update])
        print("Successfully processed update")
        return "OK", 200
    except Exception as e:
        print(f"ERROR processing update: {e}")
        return "Internal Server Error", 500

# -- این بخش باید در فایل مجزا یا در انتها باشد تا همه route ها کامل شوند --
# -- در حال حاضر فقط تست اولیه اتصال با /start را انجام می دهد --
# -- منطق Force Join و Copy Message باید اضافه شود --

@bot.message_handler(commands=["start"])
def start(m):
    print(f"START HANDLER HIT: {m.text} from chat ID: {m.chat.id}")
    try:
        # اینجا باید منطق Force Join و سپس Copy Message بیاید
        # فعلا فقط یک پیام تست ارسال می کنیم
        member = bot.get_chat_member("@pouforce", m.from_user.id) # فرض می کنیم @pouforce کانال مقصد است
        print("MEMBER STATUS:", member.status)

        # اگر عضو بود، پیام را کپی کن
        # این قسمت نیاز به message_id از deep link دارد
        # برای تست اولیه، یک پیام ثابت را ارسال می کنیم
        # bot.copy_message(m.chat.id, "@uploderrrrrr", <MESSAGE_ID_HERE>)

        bot.send_message(m.chat.id, "بات آنلاین است و عضویت شما تایید شد. آماده دریافت دستورات هستید.")
        print(f"Sent confirmation message to chat ID: {m.chat.id}")

    except telebot.apihelper.ApiTelegramException as e:
        print(f"TELEGRAM API ERROR in start handler: {e}")
        if "bot is not a member" in str(e).lower() or "chat not found" in str(e).lower():
             bot.send_message(m.chat.id, "خطا: ربات عضو کانال مقصد نیست یا کانال پیدا نشد. لطفاً ربات را ادمین کانال @pouforce کنید.")
        elif "kicked from" in str(e).lower() or "restricted" in str(e).lower():
             bot.send_message(m.chat.id, "خطا: ربات از کانال مقصد حذف شده یا دسترسی آن محدود شده است.")
        else:
             bot.send_message(m.chat.id, f"خطای تلگرام: {e}")
    except Exception as e:
        print(f"GENERAL ERROR in start handler: {e}")
        bot.send_message(m.chat.id, f"خطای پیش‌بینی نشده: {e}")
