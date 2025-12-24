from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import requests
import os

BOT_TOKEN = "PUT_YOUR_BOT_TOKEN_HERE"

NSFW_API = "https://api.sightengine.com/1.0/check.json"
API_USER = "YOUR_SIGHTENGINE_USER"
API_SECRET = "YOUR_SIGHTENGINE_SECRET"

async def scan_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        return

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)

    image_path = "image.jpg"
    await file.download_to_drive(image_path)

    response = requests.post(
        NSFW_API,
        data={
            'models': 'nudity',
            'api_user': API_USER,
            'api_secret': API_SECRET
        },
        files={'media': open(image_path, 'rb')}
    ).json()

    nudity = response.get("nudity", {})
    unsafe = nudity.get("raw", 0) > 0.6

    if unsafe:
        await update.message.delete()
        await update.message.reply_text("⚠️ NSFW content detected. Image deleted.")

    os.remove(image_path)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.PHOTO, scan_image))
app.run_polling()
