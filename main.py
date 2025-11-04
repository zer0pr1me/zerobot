from fastapi import FastAPI, Request

app = FastAPI() 

@app.post(f"/webhook/{{secret}}")
async def telegram_webhook(secret: str, request: Request):
    if secret != 'HELLOWORLD':
        return { 'ok': False }

    print("Hello there")

    return { 'ok': True}
