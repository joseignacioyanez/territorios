import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler # type: ignore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'    
)

CHAT_ID_ADMIN = 334575560

async def start (update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Comando /start sin argumentos - Ignorar
    if not context.args:
        pass
    # Comando /start con argumento incompleto - Ignorar
    if context.args[0] == "report":
        pass
    # Comando /start con argumento completo
    else:
        codigo_sordo = context.args[0].split('_')[1]
        # Responder a Usuario
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Por favor indícame lo que hace falta corregir con el sordo {codigo_sordo}. Gracias!")
        # Informar a Administrador
        await context.bot.send_message(chat_id=CHAT_ID_ADMIN, text=f"⚠️ Reporte - {codigo_sordo} --- {update.effective_user.username} - {update.effective_chat.id}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ignorar mensajes del Administrador    
    if update.effective_chat.id == CHAT_ID_ADMIN:
        pass
    else:
        # Verificar Tipos de Mensaje
        print(update.message)
        print(update.message.location)
        if update.message.location:
            # Informar a Administrador
            await context.bot.send_message(chat_id=CHAT_ID_ADMIN, text=f"📍 Ubicación - {update.effective_user.username} - {update.effective_chat.id}")
            # Reenviar ubicacion
            await context.bot.send_location(chat_id=CHAT_ID_ADMIN, latitude=update.message.location.latitude, longitude=update.message.location.longitude)
        else:
            # Responder a Usuario
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Mensaje recibido. ¿En qué más puedo ayudarte?")
            # Informar a Administrador
        await context.bot.send_message(chat_id=334575560, text=update.message.text)


if __name__ == '__main__':
    application = ApplicationBuilder().token("5937302183:AAHxqvoy9UjAIVIMlDUp6J7ny6y3D8X9brw").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler( filters.ALL, echo))

    application.run_polling()