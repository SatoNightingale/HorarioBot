import json
from datetime import date, timedelta, datetime
import pytz
from telegram import (
    Update
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
import dotenv
import os
import logging
import asyncio
from aiohttp import web
# from starlette.responses import PlainTextResponse
# import uvicorn
from dias import Dia, cargar_horario


# ---------------------------------------------------------- #
#                  Declaración de variables                  #
# ---------------------------------------------------------- #

# webhook_url = 'https://horario-bot.vercel.app/api/webhook'
# webhook_url = 'https://orarioot-satonightingale8475-5azc4xb4.leapcell.online/api/webhook'
RENDER_URL = 'https://horariobot.onrender.com'

HEALTH_PATH = "/healthz"

dotenv.load_dotenv('.env')

# bot: Application

cuba_tz = pytz.timezone('America/Havana')

datos = json.load(open('datos.json', encoding='utf-8'))
horario = cargar_horario()


# ---------------------------------------------------------- #
#                         ASYNCIO_APP                        #
# ---------------------------------------------------------- #

aio_app = web.Application()

async def health(request):
    return web.Response(text="OK", status=200)

aio_app.router.add_get(HEALTH_PATH, health)

# Opcional: una ruta GET en la raíz que devuelva algo simple
async def index(request):
    return web.Response(text="Servicio telegram en Render", status=200)

aio_app.router.add_get("/", index)



# ---------------------------------------------------------- #
#                     Funciones útiles                       #
# ---------------------------------------------------------- #

def convertir_fecha(fecha: datetime) -> date:
    fecha_convertida = fecha.astimezone(cuba_tz)
    return fecha_convertida.date()


def que_toca_dia(fecha: date) -> Dia | None:
    if fecha.isoformat() in horario:
        return horario[fecha.isoformat()]
    else:
        return None

def que_toca_hoy(hoy: date) -> Dia | None:
    return que_toca_dia(hoy)

def que_toca_manana(hoy: date) -> Dia | None:
    return que_toca_dia(hoy + timedelta(days=1))

def que_toca_semana(hoy: date) -> list[Dia]:
    ultimo_lunes = hoy - timedelta(days=hoy.weekday())
    dias_semana = []
    for i in range(5):
        dias_semana.append(que_toca_dia(ultimo_lunes + timedelta(days=i)))
    return dias_semana



# ---------------------------------------------------------- #
#                Funciones de comandos del bot               #
# ---------------------------------------------------------- #

async def command_hoy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("hoy")
    text = que_toca_hoy(convertir_fecha(update.message.date))
    if text:
        text = str(text)
    else:
        text = 'Hoy no hay clases'
    await context.bot.send_message(update.effective_chat.id, text)


async def command_manana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("manana")
    text = que_toca_manana(convertir_fecha(update.message.date))
    if text:
        text = str(text)
    else:
        text = 'Mañana no hay clases'
    await context.bot.send_message(update.effective_chat.id, text)


async def command_semana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info("semana")
    semana = que_toca_semana(convertir_fecha(update.effective_message.date))
    text = 'Horario de esta semana:\n' + '\n\n'.join([str(d) for d in semana])
    await context.bot.send_message(update.effective_chat.id, text)


# ---------------------------------------------------------- #
#                            MAIN                            #
# ---------------------------------------------------------- #

# Pa setear webhook
# curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook -d "url=https://<DOMAIN>/api/webhook"

async def start_bot():
    TOKEN = os.getenv('TOKEN')
    PORT = os.getenv("PORT", '8080')
    WEBHOOK_PATH = f"/webhook/{TOKEN}"

    webhook_url = f'{RENDER_URL}{WEBHOOK_PATH}'

    bot = Application.builder().token(TOKEN).build()

    bot.add_handler(CommandHandler('hoy', command_hoy))
    bot.add_handler(CommandHandler('manana', command_manana))
    bot.add_handler(CommandHandler('semana', command_semana))

    await bot.initialize()
    await bot.bot.set_webhook(webhook_url)
    await bot.start()

    runner = web.AppRunner(aio_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

    async def telegram_post(request):
        try:
            data = await request.json()
        except Exception:
            return web.Response(status=400, text="bad request")

        update = Update.de_json(data, bot.bot)
        # Enviar el update para que lo procese el dispatcher
        await bot.update_queue.put(update)
        return web.Response(status=200, text="OK")

    aio_app.router.add_post(WEBHOOK_PATH, telegram_post)

    logging.info("✅ Iniciado")

    # Mantener el servicio vivo
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        pass