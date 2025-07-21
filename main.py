import os
import re
import tempfile
import yt_dlp
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from threading import Thread

# Muhitdan token va webhook URLni olish
TOKEN = os.environ.get("8043474459:AAGdaiNeLpC4MDpdnXOtXueZJ9aGS7K9zLE")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# Flask server (uptime uchun)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run_flask():
    app.run(host="0.0.0.0", port=8080)

Thread(target=run_flask).start()

# Telegram bot komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("🎬 Salom! Video havolasini yuboring (YouTube, TikTok, Instagram)...")

# Format chiqarish
def extract_formats(url: str):
    ydl_opts = {"quiet": True, "skip_download": True, "forcejson": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get("formats", [])
        return [f for f in formats if f.get("filesize") and f.get("format_id")]

# Formatlar tugmalari
def format_buttons(url: str, formats):
    buttons = []
    for fmt in formats:
        size = int(fmt['filesize']) // 1024
        label = f"{fmt['format_id']} - {fmt.get('ext')} - {size} KB"
        buttons.append([InlineKeyboardButton(label, callback_data=f"{url}|{fmt['format_id']}")])
    return InlineKeyboardMarkup(buttons[:10])

# Foydalanuvchi yuborgan URLni qayta ishlash
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    if not re.match(r"https?://", url):
        await update.message.reply_text("❌ Iltimos, to'g'ri video havolasini yuboring.")
        return
    try:
        formats = extract_formats(url)
        if not formats:
            await update.message.reply_text("❌ Formatlar topilmadi yoki video mavjud emas.")
            return
        markup = format_buttons(url, formats)
        await update.message.reply_text("📥 Yuklab olish formatini tanlang:", reply_markup=markup)
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik yuz berdi: {e}")

# Tugmani bosganda video yuklab berish
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    url, format_id = query.data.split("|")
    path = tempfile.mktemp()

    ydl_opts = {
        "format": format_id,
        "outtmpl": path,
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        with open(path, "rb") as f:
            await query.message.reply_video(f)
    except Exception as e:
        await query.message.reply_text(f"❌ Yuklab olishda xatolik: {e}")
    finally:
        if os.path.exists(path):
            os.remove(path)

# Telegram botni ishga tushirish
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))

if __name__ == '__main__':
    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        webhook_url=WEBHOOK_URL,
    )

