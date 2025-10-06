import dotenv
import os
import logging
logging.info("Probando que funciona el logging")
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler
from aiohttp import web
from script import initialize_script, cleanup_script, command_hoy, command_manana, command_semana


# ---------------------------------------------------------- #
#                  Declaración de variables                  #
# ---------------------------------------------------------- #

dotenv.load_dotenv('.env')

TOKEN = os.getenv('TOKEN')
PORT = os.getenv("PORT", '8080') # render

# webhook_url = 'https://horario-bot.vercel.app/api/webhook'
# webhook_url = 'https://orarioot-satonightingale8475-5azc4xb4.leapcell.online/api/webhook'
RENDER_URL = 'https://horariobot.onrender.com'
HEALTH_PATH = "/healthz"
WEBHOOK_PATH = f"/webhook/{TOKEN}"

# App aiohttp para exponer healthcheck y montar el webhook
aio_app = web.Application()

# Health endpoint para UptimeRobot
async def health(request):
    return web.Response(text="OK", status=200)

# Opcional: una ruta GET en la raíz que devuelva algo simple
async def index(request):
    return web.Response(text="Servicio telegram en Render", status=200)

# El webhook handler para telegram: PTB expone su propia ruta cuando se usa run_webhook,
# pero aquí montamos manualmente una ruta POST que redirige a PTB para procesarla.
# PTB permite recibir raw updates vía bot.process_update, pero lo más sencillo es usar
# el método update_queue POST handling. A continuación una implementación directa para POST.
async def telegram_post(request):
    global telegram_app

    try:
        data = await request.json()
    except Exception:
        return web.Response(status=400, text="bad request")

    update = Update.de_json(data, telegram_app.bot)
    # Enviar el update para que lo procese el dispatcher
    await telegram_app.update_queue.put(update)
    return web.Response(status=200, text="OK")


aio_app.router.add_get("/", index)
aio_app.router.add_get(HEALTH_PATH, health)
aio_app.router.add_post(WEBHOOK_PATH, telegram_post)
aio_app.on_shutdown.append(cleanup_script)


# Pa setear webhook
# curl -X POST https://api.telegram.org/bot<TOKEN>/setWebhook -d "url=https://<DOMAIN>/api/webhook"

async def start_bot():
    logging.info("llamada a start_bot")
    # Inicializar código de aplicación
    initialize_script()
    logging.info("script inicializado")
    # Crear la aplicación de telegram
    global telegram_app
    telegram_app = Application.builder().token(TOKEN).build()

    telegram_app.add_handler(CommandHandler('hoy', command_hoy))
    telegram_app.add_handler(CommandHandler('manana', command_manana))
    telegram_app.add_handler(CommandHandler('semana', command_semana))
    logging.info("bot creado, handlers añadidos")
    webhook_url = f'{RENDER_URL}{WEBHOOK_PATH}'
    # Aquí usamos run_webhook pero sin bloquear el hilo principal: lo lanzamos como tarea
    await telegram_app.initialize()
    # Establecer el webhook en Telegram (setWebhook)
    await telegram_app.bot.set_webhook(webhook_url)
    # Arrancar el dispatcher del bot sin bloquear: start() prepara y start_polling/start_webhook manejan io internamente
    await telegram_app.start()
    logging.info("iniciada app de telegram")
    # Dejar el bot corriendo. run_webhook normalmente arranca su propio servidor;
    # en este ejemplo usaremos aiohttp + runner para servir la misma app que usará telegram
    runner = web.AppRunner(aio_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

    

    logging.info("✅ Iniciado")

    # Mantener el servicio vivo
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    # Ejecutar todo en el loop principal
    asyncio.run(start_bot())