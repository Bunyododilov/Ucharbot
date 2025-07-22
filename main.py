import os
from flask import Flask, request
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
from utils import download_video

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)
bot_app = ApplicationBuilder().token(BOT_TOKEN).build()

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎥 Video yuklab beruvchi botga xush kelibsiz!\nYouTube, TikTok yoki Instagram havolasini yuboring.")

# Video link handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    chat_id = update.message.chat.id

    if any(domain in url for domain in ["youtube.com", "youtu.be", "tiktok.com", "instagram.com"]):
        msg = await update.message.reply_text("⬇️ Yuklab olinmoqda, kuting...")

        try:
            filename, title = download_video(url)
            with open(filename, "rb") as video:
                await context.bot.send_video(chat_id=chat_id, video=video, caption=title)

            os.remove(filename)
        except Exception as e:
            await context.bot.send_message(chat_id=chat_id, text=f"❌ Xatolik yuz berdi: {str(e)}")
    else:
        await update.message.reply_text("❗ Iltimos, YouTube, TikTok yoki Instagram havolasini yuboring.")

# Register handlers
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Webhook
@app.route("/webhook", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    await bot_app.process_update(update)
    return "ok"

# Webhook ni sozlash
@app.route("/", methods=["GET"])
async def set_webhook():
    await bot_app.bot.set_webhook(url=WEBHOOK_URL + "/webhook")
    return "Webhook set!"

# Run Flask app
if __name__ == "__main__":
    app.run(port=10000)
