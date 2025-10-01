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
from fastapi import FastAPI
from starlette.responses import PlainTextResponse
import uvicorn
from dias import Dia, cargar_horario


# ---------------------------------------------------------- #
#                  Declaración de variables                  #
# ---------------------------------------------------------- #

# webhook_url = 'https://horario-bot.vercel.app/api/webhook'
# webhook_url = 'https://orarioot-satonightingale8475-5azc4xb4.leapcell.online/api/webhook'
webhook_url = 'https://horariobot.onrender.com'

dotenv.load_dotenv('.env')

bot: Application

server_pellizco = FastAPI()

cuba_tz = pytz.timezone('America/Havana')

datos = json.load(open('datos.json', encoding='utf-8'))
horario = cargar_horario()


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

    bot = Application.builder().token(TOKEN).build()

    bot.add_handler(CommandHandler('hoy', command_hoy))
    bot.add_handler(CommandHandler('manana', command_manana))
    bot.add_handler(CommandHandler('semana', command_semana))

    port = os.environ.get('PORT')

    bot.run_webhook(
        listen='0.0.0.0',
        port=port,
        url_path='',
        webhook_url=webhook_url,
        allowed_updates=Update.ALL_TYPES
    )

    logging.info("✅ Iniciado")


async def start_server():
    config = uvicorn.Config(server_pellizco, host='0.0.0.0', port=8080)
    server = uvicorn.Server(config)
    await server.serve()


@server_pellizco.get('/', response_class=PlainTextResponse)
async def ping():
    return 'Bot pellizcado'


async def main():
    await asyncio.gather(start_bot(), start_server())


if __name__ == "__main__":
    asyncio.run(main())