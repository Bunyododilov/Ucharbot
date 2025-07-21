import os
import yt_dlp
from flask import Flask, request
from telegram import (
    Bot,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

bot = Bot(TOKEN)
app = Flask(__name__)

# Kanalga a'zo bo'lganligini tekshiruvchi funksiya
async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

# Start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    subscribed = await check_subscription(user_id)
    if not subscribed:
        keyboard = [[InlineKeyboardButton("🔔 Kanalga obuna bo‘lish", url=f"https://t.me/{CHANNEL_USERNAME.lstrip('@')}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("❌ Koddan foydalanishdan oldin kanalimizga obuna bo‘ling.", reply_markup=reply_markup)
    else:
        await update.message.reply_text("✅ Video link yuboring (YouTube, TikTok, Instagram):")

# Video yuklash
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user_id = update.effective_user.id

    if not await check_subscription(user_id):
        await update.message.reply_text("❌ Koddan foydalanishdan oldin kanalimizga obuna bo‘ling.")
        return

    await update.message.reply_text("⏳ Yuklanmoqda, biroz kuting...")

    try:
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': 'video.%(ext)s',
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = ydl.prepare_filename(info)

        await update.message.reply_video(video=open(file_name, 'rb'), caption=info.get("title", "Video"))
        os.remove(file_name)
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {e}")

# Webhookni o‘rnatish
@app.route("/", methods=["GET", "HEAD"])
def index():
    return "Bot ishlamoqda!"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.update_queue.put_nowait(update)
    return "OK"

# Bot application
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

# Webhook o‘rnatish
async def set_webhook():
    await bot.set_webhook(f"{WEBHOOK_URL}/{TOKEN}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(set_webhook())
    application.run_polling = lambda *args, **kwargs: None  # to disable polling
    app.run(host="0.0.0.0", port=8080)
