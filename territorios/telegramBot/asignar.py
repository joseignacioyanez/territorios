"""

"""

import datetime
import locale
import logging
import time
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
import requests
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

PUBLICADOR, VERIFICACION, TERRITORIO, METODO_ENVIO = range(4)

CHAT_ID_ADMIN = 334575560

# Maneja /asignar . Empieza el proceso de asignación de territorios
async def asignar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    #  Usar Vistas de la App de Django

    # Determinar ID de Usuario en base al ChatID de Telegram
    try:
        url = 'http://localhost:8000/webTerritorios/usuario_telegram/'
        myobj = {'telegram_chatid': update.message.chat_id}
        usuario_telegram_response =  requests.post(url, json = myobj)
        json_response = usuario_telegram_response.json()
        user_id = json_response['user_id']
    except:
        await update.message.reply_text(
            "No se reconoce este usuario. Por favor contacta a un administrador."
        )
        return ConversationHandler.END

    # Determinar si el usuario tiene permisos de Administrador o Asignador
    try:
        url = 'http://localhost:8000/webTerritorios/usuario/'
        myobj = {'user_id': user_id}
        user_data_response =  requests.post(url, json = myobj)
        user_data_json = user_data_response.json()
        context.user_data['user_data'] = user_data_json
    except:
        await update.message.reply_text(
            "Error al determinar permisos del Usuario. Por favor contacta a un administrador."
        )
        return ConversationHandler.END
    
    if 'administradores' or 'asignadores' in user_data_json['groups']:

        # Obtener Lista de Publicadores Activos de la misma Congregación
        try:
            url = 'http://localhost:8000/webTerritorios/publicadores/'
            myobj = {'user_id': user_id}
            publicadores_response =  requests.post(url, json = myobj)
            publicadores_json = publicadores_response.json()
        except:
            await update.message.reply_text(
                "Error al obtener la lista de Publicadores. Por favor contacta a un administrador."
            )
            return ConversationHandler.END
    
        reply_keyboard = []
        for publicador in publicadores_json:
            reply_keyboard.append([str(publicador['id']) + ' - ' + publicador['nombre']])

        await update.message.reply_text(
            f"🙋🏻¡Hola {user_data_json['nombre']}! Te ayudaré a asignar un territorio. "
            "Envía /cancelar si deseas dejar de hablar conmigo.\n\n"
            "Escoge el Publicador al que deseas asignar el territorio:",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Escoge el Publicador..."
            ),
        )

        return PUBLICADOR
    else:
        await update.message.reply_text(
            "No tienes permisos para asignar territorios. Por favor contacta a un administrador."
        )
        return ConversationHandler.END

    

async def publicador(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda el Publicador, valida que no existan otras asignaciones y pregunta por el Territorio."""
    context.user_data['publicador_asignar_id'] = update.message.text.split(' - ')[0]
    context.user_data['publicador_asignar_nombre'] = update.message.text.split(' - ')[1]
    logger.info("Publicador a Asignar: %s", update.message.text)

    # Averiguar si el usuario tiene Asignaciones Pendientes de entregar
    try:
        url = 'http://localhost:8000/webTerritorios/asignacion_pendiente/'
        myobj = {'publicador_id': context.user_data['publicador_asignar_id']}
        asignacion_pendiente_response =  requests.post(url, json = myobj)
        asignacion_pendiente_json = asignacion_pendiente_response.json()
    except:
        await update.message.reply_text(
            "Error al obtener la lista de Asignaciones. Por favor contacta a un administrador."
        )
        return ConversationHandler.END
    
    if asignacion_pendiente_json['asignacion_pendiente']:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        fecha_obj = datetime.datetime.fromisoformat(asignacion_pendiente_json['asignacion_data']['fecha_asignacion'][:-1])  # Eliminamos la 'Z' al final
        fecha_formateada = fecha_obj.strftime("%d de %B del %Y")
        await update.message.reply_text(
f'''
El Publicador seleccionado tiene una asignación pendiente. \n
*Territorio:* {str(asignacion_pendiente_json['asignacion_data']['territorio_numero'])} - {asignacion_pendiente_json['asignacion_data']['territorio_nombre']}
*Fecha de Asignación:*  {fecha_formateada} \n
Por favor, recuérdale al Publicador e indica si deseas hacer la nueva asignación.
''',
            parse_mode='markdown',
            reply_markup=ReplyKeyboardMarkup(
                [['¡Sí, hagámoslo!'], ['No, gracias']], one_time_keyboard=True, input_field_placeholder="¿Deseas asignar igual?"
            ),
        )
    else:
        await update.message.reply_text(
            "No hay asignaciones pendientes para el Publicador seleccionado. \n ¿Deseas continuar con la asignación?",
            reply_markup=ReplyKeyboardMarkup(
                [['¡Sí, hagámoslo!'], ['No, gracias']], one_time_keyboard=True, input_field_placeholder="¿Deseas asignar?"
            ),
        )
    
    return VERIFICACION
    

async def verificacion(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Maneja la respuesta de Verificacion de Asignaciones Previas y Muestra Territorios Disponibles"""
    
    if update.message.text == 'No, gracias':
        await update.message.reply_text(
            "Está bien. Ten un buen día."
        )
        return ConversationHandler.END
    
    else:
        
        # Obtener Lista de Territorios Disponibles
        try:
            url = 'http://localhost:8000/webTerritorios/territorios_disponibles/'
            myobj = {'id_congregacion': context.user_data['user_data']['congregacion_id']}
            territorios_disponibles_response =  requests.post(url, json = myobj)
            territorios_disponibles_json = territorios_disponibles_response.json()

            reply_keyboard = []
            for territorio in territorios_disponibles_json['territorios']:
                reply_keyboard.append([str(territorio['numero']) + ' - ' + territorio['nombre']])

            # Guardar lista de Territorios en Contexto para acceder despues
            context.user_data['territorios_disponibles'] = territorios_disponibles_json['territorios']            

            await update.message.reply_text(
                f"Escoge el Territorio que deseas asignar al Publicador:",
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True, input_field_placeholder="Escoge el Territorio..."
                ),
            )

            return TERRITORIO
        
        except:
            await update.message.reply_text(
                "Error al obtener la lista de Territorios. Por favor contacta a un administrador."
            )
            return ConversationHandler.END


async def territorio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda el Territorio y pregunta por el Método de Entrega."""

    territorio_numero_deseado = update.message.text.split(' - ')[0]
    territorio_nombre_deseado = update.message.text.split(' - ')[1]
    
    for territorio in context.user_data['territorios_disponibles']:
        if str(territorio['numero']) == territorio_numero_deseado and territorio['nombre'] == territorio_nombre_deseado:
            context.user_data['territorio_asignar_id'] = territorio['id']
            context.user_data['territorio_asignar_numero_nombre'] = str(territorio['numero']) + ' - ' + territorio['nombre']
            break

    await update.message.reply_text(
f'''
¡Buena elección! Por último... \n
¿Cómo deseas que se entregue el territorio?.
''',
            parse_mode='markdown',
            reply_markup=ReplyKeyboardMarkup(
                [['Enviar al Telegram del herman@'], 
                    ['Registrar asignación y Enviarme el PDF digital por aquí'], 
                    ['Registrar asignación y Enviarme el PDF para Imprimir por aquí']], one_time_keyboard=True, input_field_placeholder="¿Cómo entregar?"
            ),
        )
        
    return METODO_ENVIO

async def metodo_envio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Guarda el Método de Entrega y finaliza la asignación."""

    context.user_data['metodo_envio'] = update.message.text

    if context.user_data['metodo_envio'] == 'Enviar al Telegram del herman@':
        #TODO
        pass
    elif context.user_data['metodo_envio'] == 'Registrar asignación y Enviarme el PDF digital por aquí':
        #TODO
        pass
    elif context.user_data['metodo_envio'] == 'Registrar asignación y Enviarme el PDF para Imprimir por aquí':
        #TODO
        pass
    else:
        await update.message.reply_text(
            "No se reconoce el método de entrega. Por favor contacta a un administrador."
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        f"¡Excelente! \n {context.user_data['territorio_asignar_numero_nombre']} se asignó a {context.user_data['publicador_asignar_nombre']}. \n ¡Gracias por tu ayuda!", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancela y finaliza la conversación."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Adiós! Espero volvamos a conversar.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

async def reporte_asignaciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    try:
        # Determinar ID de Usuario en base al ChatID de Telegram
        url = 'http://localhost:8000/webTerritorios/usuario_telegram/'
        myobj = {'telegram_chatid': update.message.chat_id}
        usuario_telegram_response =  requests.post(url, json = myobj)
        json_response = usuario_telegram_response.json()
        user_id = json_response['user_id']
        
        # Determinar si el usuario tiene permisos de Administrador o Asignador
        url = 'http://localhost:8000/webTerritorios/usuario/'
        myobj = {'user_id': user_id}
        user_data_response =  requests.post(url, json = myobj)
        user_data_json = user_data_response.json()
        context.user_data['user_data'] = user_data_json

        if 'administradores' in user_data_json['groups']:
            
            # Obtener Lista de Asignaciones Pendientes
            url = 'http://localhost:8000/webTerritorios/asignaciones_pendientes/'
            myobj = {'id_congregacion': user_data_json['congregacion_id']}
            asignaciones_pendientes_response =  requests.post(url, json = myobj)
            asignaciones_pendientes_json = asignaciones_pendientes_response.json()

            encabezado = "📋 *Asignaciones Pendientes* \n\n"

            keyboard = []

            for asignacion in asignaciones_pendientes_json['asignaciones']:
                territorio = str(asignacion['territorio_numero']) + '-' + asignacion['territorio_nombre']
                publicador = asignacion['publicador_nombre']

                current_date = datetime.datetime.now().date()
                given_date = datetime.datetime.fromisoformat(asignacion['fecha_asignacion'][:-1]).date()
                days_since_date = (current_date - given_date).days
                
                boton_asignacion = ""

                if days_since_date < 14:
                    boton_asignacion += f"🟢"
                elif days_since_date < 21:
                    boton_asignacion += f"🟡"
                else:
                    boton_asignacion += f"🔴"
                
                boton_asignacion += f" {days_since_date} días | {territorio} -> {publicador}"

                # Callback Data
                callback_data = ""
                # 1. Timestamp epoch
                callback_data += str(int(time.time()))
                # 2. Flag Proceso
                callback_data += ";reporte_asignaciones;"
                # 3. ID Asignacion
                callback_data += f"{asignacion['id']}"


                keyboard.append([InlineKeyboardButton(boton_asignacion, callback_data=callback_data)])       

            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                encabezado,
                reply_markup=reply_markup,
                parse_mode='markdown'
            )
        else:
            await update.message.reply_text(
                "No tienes permisos para ver este reporte. Por favor contacta a un administrador."
            )
            return ConversationHandler.END

    except Exception as e:
        print(e)
        await update.message.reply_text(
            "No se reconoce este usuario. Por favor contacta a un administrador."
        )
        return ConversationHandler.END

async def inline_button_asignaciones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    timestamp = query.data.split(';')[0]
    flag_proceso = query.data.split(';')[1]
    dato = query.data.split(';')[2]

    # Ignorar Queries de mas de 5 minutos
    if int(time.time()) - int(timestamp) > 300:
        pass
    else:
        if flag_proceso == "reporte_asignaciones":
            # Obtener detalles de asignacion
            url = 'http://localhost:8000/webTerritorios/asignacion_detalles/'
            myobj = {'id_asignacion': dato}
            asignacion_detalles_response =  requests.post(url, json = myobj)
            asignacion_detalles_json = asignacion_detalles_response.json()

            await query.message.reply_text(text=f"Asignacion: {query.data}")

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
        elif update.message.voice:
            file_id = update.message.voice.file_id
            await context.bot.send_message(chat_id=CHAT_ID_ADMIN, text=f"💬 {update.effective_user.username} - {update.effective_chat.id} - 🎤 Audio")
            await context.bot.send_voice(chat_id=CHAT_ID_ADMIN, voice=file_id)
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


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("5937302183:AAHxqvoy9UjAIVIMlDUp6J7ny6y3D8X9brw").build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("asignar", asignar)],
        states={
            PUBLICADOR: [MessageHandler(filters.Regex("^(?!\/cancelar$).*"), publicador), CommandHandler("cancelar", cancelar)],
            VERIFICACION: [MessageHandler(filters.Regex("^(?!\/cancelar$).*"), verificacion), CommandHandler("cancelar", cancelar)],
            TERRITORIO: [MessageHandler(filters.Regex("^(?!\/cancelar$).*"), territorio), CommandHandler("cancelar", cancelar)],
            METODO_ENVIO: [MessageHandler(filters.Regex("^(?!\/cancelar$).*"), metodo_envio), CommandHandler("cancelar", cancelar)]
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )
    application.add_handler(conv_handler)

    application.add_handler(CommandHandler("reporteAsignaciones",reporte_asignaciones))
    application.add_handler(CallbackQueryHandler(inline_button_asignaciones))

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler( filters.ALL, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()