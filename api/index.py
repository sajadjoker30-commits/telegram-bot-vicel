from flask import Flask, request
import telebot, os, json

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set in Vercel environment variables")

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

# -- تنظیمات کانال ها --
# *** لطفاً مطمئن شوید که این نام کانال ها دقیقاً درست هستند ***
TARGET_CHANNEL_USERNAME = "@pouforce" # کانالی که کاربر باید عضو شود
SOURCE_CHANNEL_USERNAME = "@uploderrrrrr" # کانالی که ویدئو از آن کپی می شود

# -- تعریف مسیر وب هوک --
@app.route("/", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # برای تست اینکه وب هوک فعال است
        return "Bot is running!", 200

    if request.method == "POST":
        try:
            # دریافت داده خام و سپس تبدیل به آبجکت Update
            update = telebot.types.Update.de_json(request.get_data(as_text=True))
            bot.process_new_updates([update])
            return "OK", 200
        except Exception as e:
            print(f"Error processing webhook: {e}")
            return "Internal Server Error", 500

# -- هندلر دستور /start --
@bot.message_handler(commands=["start"])
def handle_start(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    command_text = message.text

    print(f"Received /start command from chat_id: {chat_id}, user_id: {user_id}, text: {command_text}")

    message_id_to_copy = None
    try:
        # استخراج message_id از دستور /start اگر وجود داشته باشد
        # فرمت مورد انتظار: /start <message_id> یا /start=MESSAGE_ID
        parts = command_text.split(' ', 1)
        if len(parts) > 1:
            deep_link_param = parts[1]
            # اگر پارامتر به شکل MESSAGE_ID باشد (مثلا بعد از =)، آن را استخراج می کنیم
            if '=' in deep_link_param:
                message_id_to_copy = deep_link_param.split('=', 1)[1]
            else:
                # فرض می کنیم خود پارامتر message_id است
                message_id_to_copy = deep_link_param
            print(f"Extracted message_id from deep link: {message_id_to_copy}")

    except Exception as e:
        print(f"Error extracting message_id from start command: {e}")
        # اگر نتوانستیم message_id را استخراج کنیم، ربات به کار خود ادامه می دهد اما بدون کپی پیام خاص

    # --- بخش ۱: بررسی عضویت کاربر ---
    try:
        # بررسی عضویت کاربر در کانال مقصد
        chat_member = bot.get_chat_member(TARGET_CHANNEL_USERNAME, user_id)
        print(f"User {user_id} status in {TARGET_CHANNEL_USERNAME}: {chat_member.status}")

        # وضعیت های عضویت: 'creator', 'administrator', 'member', 'restricted', 'left', 'kicked'
        if chat_member.status not in ['creator', 'administrator', 'member']:
            bot.send_message(chat_id, f"برای استفاده از ربات، لطفاً ابتدا عضو کانال ما شوید:\n{TARGET_CHANNEL_USERNAME}")
            print(f"User {user_id} is not a member of {TARGET_CHANNEL_USERNAME}. Sent join message.")
            return # خروج از تابع اگر عضو نیست

    except telebot.apihelper.ApiTelegramException as e:
        print(f"Telegram API Error checking membership for user {user_id}: {e}")
        # اگر ربات ادمین نباشد یا کانال private باشد و ربات عضو نباشد، این خطا رخ می دهد
        bot.send_message(chat_id, f"خطا در بررسی عضویت. لطفاً مطمئن شوید ربات در کانال {TARGET_CHANNEL_USERNAME} حداقل دسترسی لازم را دارد (مثلاً ادمین یا عضو).")
        return # خروج اگر خطای API رخ داد
    except Exception as e:
        print(f"General error checking membership for user {user_id}: {e}")
        bot.send_message(chat_id, "خطای غیرمنتظره در بررسی عضویت.")
        return # خروج برای خطاهای عمومی

    # --- بخش ۲: اگر کاربر عضو بود، پیام را کپی کن ---
    if message_id_to_copy:
        try:
            print(f"Attempting to copy message {message_id_to_copy} from {SOURCE_CHANNEL_USERNAME} to chat {chat_id}")
            # کپی کردن پیام از کانال منبع به چت کاربر
            # این تابع پیام را بدون واترمارک فوروارد ارسال می کند
            copied_message = bot.copy_message(chat_id, SOURCE_CHANNEL_USERNAME, message_id_to_copy)
            print(f"Successfully copied message {message_id_to_copy} to chat {chat_id}")

        except telebot.apihelper.ApiTelegramException as e:
            print(f"Telegram API Error copying message {message_id_to_copy}: {e}")
            if "message not found" in str(e).lower():
                bot.send_message(chat_id, "خطا: پیام مورد نظر در کانال منبع یافت نشد. ممکن است شناسه پیام اشتباه باشد یا پیام حذف شده باشد.")
            elif "chat not found" in str(e).lower() or "bot is not a member" in str(e).lower():
                 bot.send_message(chat_id, f"خطا: کانال منبع {SOURCE_CHANNEL_USERNAME} یافت نشد، ربات به آن دسترسی ندارد، یا پیام در آن کانال نیست. لطفاً دسترسی ربات به کانال منبع را بررسی کنید.")
            else:
                bot.send_message(chat_id, f"خطای تلگرام در ارسال پیام: {e}")
        except Exception as e:
            print(f"General error copying message {message_id_to_copy}: {e}")
            bot.send_message(chat_id, "خطای غیرمنتظره در ارسال پیام.")
    else:
        # اگر message_id_to_copy وجود نداشت (یعنی کاربر بدون deep link استارت زد)
        bot.send_message(chat_id, "عضویت شما تایید شد. برای دریافت ویدئو، لطفاً از لینکی که حاوی شناسه پیام است استفاده کنید.")
        print(f"User {user_id} is a member but no message_id was provided via deep link.")
