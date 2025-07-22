import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import yt_dlp

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
CHANNEL_USERNAMES = os.getenv("CHANNEL_USERNAMES", "").split(",")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_user_subscribed(bot, user_id):
    for channel in CHANNEL_USERNAMES:
        try:
            member = bot.get_chat_member(chat_id=channel.strip(), user_id=user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except Exception as e:
            logger.error(f"Subscription check failed for {channel}: {e}")
            return False
    return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_user_subscribed(context.bot, user.id):
        text = "Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:\n"
        for ch in CHANNEL_USERNAMES:
            text += f"👉 {ch.strip()}\n"
        text += "Obuna bo‘lgach /start ni qayta yuboring."

        await update.message.reply_text(text)
        return

    await update.message.reply_text("Linkni yuboring: YouTube, TikTok yoki Instagram.")


async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_user_subscribed(context.bot, user.id):
        await start(update, context)
        return

    url = update.message.text.strip()

    ydl_opts = {
        'format': 'mp4',
        'outtmpl': 'video.%(ext)s',
        'quiet': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get("url", None)
            title = info.get("title", "video")

            await update.message.reply_video(
                video=video_url,
                caption=f"{title}",
                supports_streaming=True
            )
    except Exception as e:
        logger.error(f"Video yuklab olishda xatolik: {e}")
        await update.message.reply_text("❌ Video yuklab bo‘lmadi. Linkni tekshiring.")


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

    async def on_startup(app):
        await app.bot.set_webhook(WEBHOOK_URL)

    app.run_webhook(
        listen="0.0.0.0",
        port=10000,
        webhook_url=WEBHOOK_URL,
        on_startup=on_startup
    )

