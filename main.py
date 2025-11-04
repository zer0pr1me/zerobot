from fastapi import FastAPI, Request
import os

app = FastAPI() 

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "HELLOWORLD")

@app.post(f"/webhook/{{secret}}")
async def telegram_webhook(secret: str, request: Request):
    if secret != WEBHOOK_SECRET:
        return { 'ok': False }

    print("Hello there")

    return { 'ok': True}
