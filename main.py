import os
import logging
import yt_dlp
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 8443))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Yuklamoqchi bo‘lgan YouTube, TikTok yoki Instagram havolasini yuboring.")

# Video yuklash
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user_id = update.message.chat_id

    if not url.startswith(("http://", "https://")):
        await update.message.reply_text("Iltimos, to‘g‘ri havola yuboring.")
        return

    # Yuborilayotganini bildir
    await update.message.reply_text("⏳ Yuklanmoqda, biroz kuting...")

    try:
        ydl_opts = {
            "outtmpl": f"{user_id}.%(ext)s",
            "format": "mp4",
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = ydl.prepare_filename(info)
            title = info.get("title", "video")

        # Foydalanuvchiga jo‘natish
        with open(video_path, "rb") as f:
            await update.message.reply_video(f, caption=f"{title}")

        os.remove(video_path)

    except Exception as e:
        logger.error(f"Xatolik: {e}")
        await update.message.reply_text("❌ Yuklab bo‘lmadi. Havola noto‘g‘ri yoki serverda muammo bor.")

# Webhook handler
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
