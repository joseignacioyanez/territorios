"""

"""

import datetime
import locale
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
import requests
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

PUBLICADOR, VERIFICACION, TERRITORIO, METODO_ENVIO = range(4)

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
        pass
    elif context.user_data['metodo_envio'] == 'Registrar asignación y Enviarme el PDF digital por aquí':
        pass
    elif context.user_data['metodo_envio'] == 'Registrar asignación y Enviarme el PDF para Imprimir por aquí':
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


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("5937302183:AAHxqvoy9UjAIVIMlDUp6J7ny6y3D8X9brw").build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("asignar", asignar)],
        states={
            PUBLICADOR: [MessageHandler(None, publicador), CommandHandler("cancelar", cancelar)],
            VERIFICACION: [MessageHandler(None, verificacion), CommandHandler("cancelar", cancelar)],
            TERRITORIO: [MessageHandler(None, territorio), CommandHandler("cancelar", cancelar)],
            METODO_ENVIO: [MessageHandler(None, metodo_envio), CommandHandler("cancelar", cancelar)]
        },
        fallbacks=[CommandHandler("cancelar", cancelar)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()