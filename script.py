import json
from datetime import date, timedelta, datetime
import pytz
from telegram import (
    Update
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)
import dotenv
import os
import logging
from dias import Dia, cargar_horario


webhook_url = 'https://horario-bot.vercel.app/'

dotenv.load_dotenv('.env')

cuba_tz = pytz.timezone('America/Havana')

datos = json.load(open('datos.json', encoding='utf-8'))
horario = cargar_horario()

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


def main():
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

    # bot.run_polling()

    logging.info("Log: Iniciado")
    print("Iniciado")


async def command_hoy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = que_toca_hoy(convertir_fecha(update.message.date))
    if text:
        text = str(text)
    else:
        text = 'Hoy no hay clases'
    await context.bot.send_message(update.effective_chat.id, text)


async def command_manana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = que_toca_manana(convertir_fecha(update.message.date))
    if text:
        text = str(text)
    else:
        text = 'Mañana no hay clases'
    await context.bot.send_message(update.effective_chat.id, text)


async def command_semana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    semana = que_toca_semana(convertir_fecha(update.effective_message.date))
    text = 'Horario de esta semana:\n' + '\n\n'.join([str(d) for d in semana])
    await context.bot.send_message(update.effective_chat.id, text)


if __name__ == "__main__":
    main()