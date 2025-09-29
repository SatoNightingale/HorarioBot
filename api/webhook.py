from fastapi import FastAPI, Request
from telegram import Update
from contextlib import asynccontextmanager
from script import init_bot

app = FastAPI()

APPLICATION = None

@asynccontextmanager
async def get_application():
    global APPLICATION
    if APPLICATION is None:
        APPLICATION = await init_bot()
        APPLICATION.initialize()
    return APPLICATION

@app.post('/')
async def webhook(request: Request):
    app_instance = await get_application()
    print("llega update")
    data = await request.json()
    update = Update.de_json(data, app_instance.bot)
    await app_instance.process_update(update)
    return {'ok': True}