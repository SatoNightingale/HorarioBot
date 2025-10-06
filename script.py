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
#               Inicialización / finalización                #
# ---------------------------------------------------------- #

def initialize():
    global cuba_tz, connection
    # Zona horaria de Cuba
    cuba_tz = pytz.timezone('America/Havana')
    # horario = cargar_horario()
    connection = sqlite3.connect("datos.db")

def cleanup():
    global connection
    connection.close()


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
    lunes = hoy - timedelta(days=hoy.weekday())
    if hoy.weekday() >= 5:
        lunes += timedelta(days=7)
    dias_semana = []
    for i in range(5):
        dias_semana.append(que_toca_dia(lunes + timedelta(days=i)))
    return dias_semana


# ---------------------------------------------------------- #
#                Funciones de comandos del bot               #
# ---------------------------------------------------------- #

async def command_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        update.effective_chat.id,
        """<strong>El bot que te dice qué toca mañana</strong>
        <i>Por Satoshi, el más raro del aula</i>

        Este bot es para consultar el horario de clases del segundo año de la carrera de Ciencias de la Computación de la UCLV
        Para usarlo, sólo pon alguno de estos comandos:
        /hoy - te dice lo que hay hoy mismo en el horario
        /manana - el horario de mañana (sí, telegram no deja ponerle la 'ñ')
        /semana - el horario de esta semana. Si es fin de semana, te dirá el horario de la semana próxima
        /excel - envía el documento Excel con el horario. Útil para comprobar, porque de todas maneras, esto puede tener errores

        Pronto pienso agregarle más cosas, y por supuesto, estoy abierto a recomendaciones. Escríbanle a @SatoNightingale si tienen algún problema, pero no lo atosiguen mucho porque estamos en pruebas (ni que él estudiara)
        """,
        parse_mode=ParseMode.HTML
    )

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

async def command_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open("P42doCC0510.xlsx", 'rb') as excel:
        await context.bot.send_document(update.effective_chat.id, document=excel)