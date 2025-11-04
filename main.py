import io
import os

import qrcode
from fastapi import FastAPI, Request
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram import BotCommand, InputFile, ReplyKeyboardMarkup, Update

# curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/setWebhook" \
#      -d "url=$PUBLIC_URL/webhook/HELLOWORLD"
BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "HELLOWORLD")


app = FastAPI() 
tg_app = Application.builder().token(BOT_TOKEN).build()

def make_qr_bytes(s: str) -> bytes:
    img = qrcode.make(s, box_size=8, border=2)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = ReplyKeyboardMarkup([["Create QR"]], resize_keyboard=True, one_time_keyboard=False)
    await update.message.reply_text(
            'Hi! Tap the button below to create QR from any text',
            reply_markup=kb)

async def start_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['awaiting_qr'] = True
    await update.message.reply_text('Send me the text/link and I\'ll return a QR.')

async def maybe_generate_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_qr') and update.message and update.message.text:
        png = make_qr_bytes(update.message.text.strip())
        context.user_data['awaiting_qr'] = False
        await update.message.reply_photo(photo=png, caption='Here you go!')

@app.on_event("startup")
async def on_startup():
    await tg_app.initialize()
    tg_app.add_handler(CommandHandler('start', start))
    tg_app.add_handler(CommandHandler('qr', start_qr))
    tg_app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r"^Create QR$"), start_qr))
    tg_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, maybe_generate_qr))
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
