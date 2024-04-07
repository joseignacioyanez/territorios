import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler # type: ignore

# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'    
# )

CHAT_ID_ADMIN = 334575560

async def start (update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Comando /start sin argumentos - Ignorar
    if not context.args:
        pass
    # Comando /start con argumento incompleto - Ignorar
    elif context.args[0] == "reportar":
        pass
    # Comando /start con argumento completo
    elif context.args[0].startswith("reportar"):
        codigo_sordo = context.args[0].split('_')[1]
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Por favor indícame lo que hace falta corregir con el sordo {codigo_sordo}. Gracias!")
        await context.bot.send_message(chat_id=CHAT_ID_ADMIN, text=f"⚠️ Reporte - {codigo_sordo} --- {update.effective_user.username} - {update.effective_chat.id}")
    elif context.args[0].startswith("entregar"):
        id_asignacion = context.args[0].split('_')[1]

        # Llamar a Funcion de Entrega
        # TODO

        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Gracias por entregar el territorio XXX !")
        await context.bot.send_message(chat_id=CHAT_ID_ADMIN, text=f"🥳 Entrega - {id_asignacion} --- {update.effective_user.username} - {update.effective_chat.id}")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ignorar mensajes del Administrador    
    if update.effective_chat.id == CHAT_ID_ADMIN:
        pass
    else:
        # Verificar Tipos de Mensajes
        if update.message.location:
            await context.bot.send_message(chat_id=CHAT_ID_ADMIN, text=f"💬 {update.effective_user.username} - {update.effective_chat.id} - 📍 Ubicación")
            await context.bot.send_location(chat_id=CHAT_ID_ADMIN, latitude=update.message.location.latitude, longitude=update.message.location.longitude)
        elif update.message.photo:
            file_id = update.message.photo[0].file_id
            caption = update.message.caption
            await context.bot.send_message(chat_id=CHAT_ID_ADMIN, text=f"💬 {update.effective_user.username} - {update.effective_chat.id} - 📸 Foto")
            await context.bot.send_photo(chat_id=CHAT_ID_ADMIN, photo=file_id, caption=caption)
        elif update.message.document:
            file_id = update.message.document.file_id
            caption = update.message.caption
            await context.bot.send_message(chat_id=CHAT_ID_ADMIN, text=f"💬 {update.effective_user.username} - {update.effective_chat.id} - 📄 Documento")
            await context.bot.send_video(chat_id=CHAT_ID_ADMIN, video=file_id, caption=caption)
        elif update.message.sticker:
            file_id = update.message.sticker.file_id
            await context.bot.send_message(chat_id=CHAT_ID_ADMIN, text=f"💬 {update.effective_user.username} - {update.effective_chat.id} - 🎨 Sticker")
            await context.bot.send_sticker(chat_id=CHAT_ID_ADMIN, sticker=file_id)
        elif update.message.contact:
            await context.bot.send_message(chat_id=CHAT_ID_ADMIN, text=f"💬 {update.effective_user.username} - {update.effective_chat.id} - 👤 Contacto")
            await context.bot.send_contact(chat_id=CHAT_ID_ADMIN, phone_number=update.message.contact.phone_number, first_name=update.message.contact.first_name)
        elif update.message.text:
            await context.bot.send_message(chat_id=CHAT_ID_ADMIN, text=f"💬 {update.effective_user.username} - {update.effective_chat.id} - 📝 Texto")
            await context.bot.send_message(chat_id=CHAT_ID_ADMIN, text=update.message.text)
        else:
            await context.bot.send_message(chat_id=CHAT_ID_ADMIN, text=f"💬 {update.effective_user.username} - {update.effective_chat.id} - 🤷‍♂️ No se pudo identificar el tipo de mensaje")
            await context.bot.send_message(chat_id=CHAT_ID_ADMIN, text=update)

def main():
    application = ApplicationBuilder().token("5937302183:AAHxqvoy9UjAIVIMlDUp6J7ny6y3D8X9brw").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler( filters.ALL, echo))

    application.run_polling()


if __name__ == '__main__':
    main()