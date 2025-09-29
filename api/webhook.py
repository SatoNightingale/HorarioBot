from fastapi import FastAPI, Request
from telegram import Update
from contextlib import asynccontextmanager
from script import init_bot

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.bot = await init_bot()

@app.post('/api/webhook')
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, app.state.bot.bot)
    await app.state.bot.process_update(update)
    return {'ok': True}