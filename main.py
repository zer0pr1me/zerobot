from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import BotCommand, ReplyKeyboardMarkup
from fastapi import FastAPI, Request
import os

# curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/setWebhook" \
#      -d "url=$PUBLIC_URL/webhook/HELLOWORLD"
BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "HELLOWORLD")


app = FastAPI() 
tg_app = Application.builder().token(BOT_TOKEN).build()

async def start(start, context):
    kb = ReplyKeyboardMarkup([["Create QR"]], resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(
            'Hi! Tap the button below to create QR from any text',
            reply_markup=kb)

@app.on_event("startup")
async def on_startup():
    await tg_app.initialize()
    tg_app.add_handler(CommandHandler('start', start))
    await tg_app.bot.set_my_commands([BotCommand('start', "Show menu"), 
                                      BotCommand('qr', "Create a QR")])


@app.post(f"/webhook/{{secret}}")
async def telegram_webhook(secret: str, request: Request):
    if secret != WEBHOOK_SECRET:
        return { 'ok': False }

    data = await request.json()
    update = Update.de_json(data, tg_app.bot)
    await tg_app.process_update(update)

    return { 'ok': True}
