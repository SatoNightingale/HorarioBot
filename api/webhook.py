from fastapi import FastAPI, Request
from telegram import Update
from script import init_bot

app = FastAPI()

@app.post("/webhook")
async def webhook(req: Request):
    bot = await init_bot()
    data = await req.json()
    update = Update.de_json(data, bot)
    # dp = Dispatcher(bot, None, workers=4)
    # register_handlers(dp)
    bot.process_update(update)
    return {"ok": True}

@app.get("/")
def read_root():
    return {"message": "OK"}
