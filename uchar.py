import os
import requests
import subprocess
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram import ReplyKeyboardMarkup

TOKEN = "8043474459:AAGdaiNeLpC4MDpdnXOtXueZJ9aGS7K9zLE"

def start(update, context):
    keyboard = [['🟢 YouTube', '🟣 TikTok', '🟠 Instagram']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        "👋 Salom! Men YouTube, TikTok va Instagram videolarini yuklab beraman.\n\n"
        "🎯 Link yuboring – men sizga videoni yuboraman.\n\n"
        "📌 Qo‘llab-quvvatlanadigan saytlardan link yuboring:\n"
        "- youtube.com\n- tiktok.com\n- instagram.com",
        reply_markup=reply_markup
    )

def download_video(update, context):
    url = update.message.text.strip()

    if "youtu" in url:
        update.message.reply_text("⏬ YouTube videosi yuklanmoqda...")
        try:
            filename = "video.mp4"
            subprocess.run(["yt-dlp", "-o", filename, url], check=True)
            with open(filename, 'rb') as video:
                update.message.reply_video(video)
            os.remove(filename)
        except Exception as e:
            update.message.reply_text(f"❌ Xatolik: {e}")

    elif "tiktok.com" in url:
        update.message.reply_text("⏬ TikTok videosi yuklanmoqda...")
        try:
            api_url = f"https://api.tiklydown.me/api/download?url={url}"
            res = requests.get(api_url).json()
            video_url = res['video']['noWatermark']
            context.bot.send_video(update.effective_chat.id, video=video_url)
        except Exception:
            update.message.reply_text("❌ TikTok videosini yuklab bo‘lmadi.")

    elif "instagram.com" in url:
        update.message.reply_text("⏬ Instagram videosi yuklanmoqda...")
        try:
            api = "https://igram.io/api/ajax"
            data = {"url": url}
            headers = {"x-requested-with": "XMLHttpRequest"}
            res = requests.post(api, data=data, headers=headers).json()
            video_url = res['data']['medias'][0]['url']
            context.bot.send_video(update.effective_chat.id, video=video_url)
        except Exception:
            update.message.reply_text("❌ Instagram videosini yuklab bo‘lmadi.")

    else:
        update.message.reply_text("❗ Iltimos, YouTube, TikTok yoki Instagram linkini yuboring.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download_video))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
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

