import os
import re
import tempfile
import yt_dlp
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler

TOKEN = ("8043474459:AAGdaiNeLpC4MDpdnXOtXueZJ9aGS7K9zLE")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

# Start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("🎬 Salom! Video havolasini yuboring (YouTube, TikTok, Instagram)...")

# Callback handler for format buttons
def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    url, format_code = query.data.split("|")
    download_video(url, query, context, format_code)

def extract_formats(url: str):
    ydl_opts = {"quiet": True, "skip_download": True, "forcejson": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get("formats", [])
        return [f for f in formats if f.get("filesize") and f.get("format_id")]

def format_buttons(url: str, formats):
    buttons = []
    for fmt in formats:
        label = f"{fmt['format_id']} - {fmt.get('ext')} - {int(fmt['filesize'])//1024} KB"
        buttons.append([InlineKeyboardButton(label, callback_data=f"{url}|{fmt['format_id']}")])
    return InlineKeyboardMarkup(buttons[:10])  # Max 10 formats for brevity

# Download video
def download_video(url: str, query, context: CallbackContext, format_id: str):
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        path = tmp_file.name
    ydl_opts = {
        "format": format_id,
        "outtmpl": path,
        "quiet": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        with open(path, "rb") as video_file:
            context.bot.send_video(chat_id=query.message.chat_id, video=video_file)
    except Exception as e:
        query.message.reply_text(f"❌ Xatolik yuz berdi: {e}")
    finally:
        if os.path.exists(path):
            os.remove(path)

# URL handler
def handle_url(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    if not re.match(r"https?://", url):
        update.message.reply_text("❌ Iltimos, to'g'ri video havolasini yuboring.")
        return
    try:
        formats = extract_formats(url)
        if not formats:
            update.message.reply_text("❌ Formatlar topilmadi yoki video mavjud emas.")
            return
        reply_markup = format_buttons(url, formats)
        update.message.reply_text("📥 Yuklab olish formatini tanlang:", reply_markup=reply_markup)
    except Exception as e:
        update.message.reply_text(f"❌ Xatolik yuz berdi: {e}")

# Webhook endpoint
@app.route("/webhook", methods=["POST"])
def webhook() -> str:
    update = Update.de_json(request.get_json(force=True), Application.builder().token(TOKEN).build().bot)
    application.process_update(update)
    return "OK"

# Bot setup
application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))

if __name__ == '__main__':
    application.run_polling()
# Fayl oxirida bo‘lishi kerak
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot ishlayapti!"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

