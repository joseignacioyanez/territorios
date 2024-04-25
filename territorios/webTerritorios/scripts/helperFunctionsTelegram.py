from telegram import Bot

async def enviar_documento(file_path, chat_id, texto):
    bot = Bot(token="5937302183:AAHxqvoy9UjAIVIMlDUp6J7ny6y3D8X9brw")
    # Send the document
    with open(file_path, 'rb') as document_file:
        await bot.send_document(chat_id=chat_id, document=document_file, caption='*Territorios*')
    return True