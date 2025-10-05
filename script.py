from datetime import date, timedelta, datetime
import pytz
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
import sqlite3
import logging
import traceback
from dias import Dia, Turno
from sql_utils import get_db_list


# ---------------------------------------------------------- #
#                          Globales                          #
# ---------------------------------------------------------- #

def initialize_script():
    global cuba_tz, connection
    # Zona horaria de Cuba
    cuba_tz = pytz.timezone('America/Havana')
    # horario = cargar_horario()
    connection = sqlite3.connect("datos.db")


# ---------------------------------------------------------- #
#                     Funciones útiles                       #
# ---------------------------------------------------------- #

def convertir_fecha(fecha: datetime) -> date:
    fecha_convertida = fecha.astimezone(cuba_tz)
    return fecha_convertida.date()


def que_toca_dia(fecha: date) -> Dia | None:
    data_turnos = get_db_list('Turno_Clase', ['num_turno', 'id_asig', 'id_mod', 'id_otro'], fecha.isoformat(), connection, prim_key_name='fecha', as_string=True)

    if len(data_turnos) > 0:
        turnos = []
        for tupla in data_turnos:
            turnos.append(Turno(fecha, tupla[0], tupla[1], tupla[2], tupla[3]))
        return Dia(fecha, turnos)
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
    try:
        text = que_toca_hoy(convertir_fecha(update.message.date))
        if text:
            text = str(text)
        else:
            text = 'Hoy no hay clases'
        await context.bot.send_message(update.effective_chat.id, text, parse_mode=ParseMode.HTML)
    except Exception as e:
        tb_str = traceback.format_exc()
        await context.bot.send_message(update.effective_chat.id, f"Ha ocurrido un error:\n{type(e).__name__} - {e}\n{tb_str}")


async def command_manana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logging.info("manana")
        text = que_toca_manana(convertir_fecha(update.message.date))
        if text:
            text = str(text)
        else:
            text = 'Mañana no hay clases'
        await context.bot.send_message(update.effective_chat.id, text, parse_mode=ParseMode.HTML)
    except Exception as e:
        tb_str = traceback.format_exc()
        await context.bot.send_message(update.effective_chat.id, f"Ha ocurrido un error:\n{type(e).__name__} - {e}\n{tb_str}")


async def command_semana(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        logging.info("semana")
        semana = que_toca_semana(convertir_fecha(update.effective_message.date))
        text = 'Horario de esta semana:\n' + '\n\n'.join([str(d) for d in semana])
        await context.bot.send_message(update.effective_chat.id, text, parse_mode=ParseMode.HTML)
    except Exception as e:
        tb_str = traceback.format_exc()
        await context.bot.send_message(update.effective_chat.id, f"Ha ocurrido un error:\n{type(e).__name__} - {e}\n{tb_str}")