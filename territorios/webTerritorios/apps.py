import subprocess
from django.apps import AppConfig
from dotenv import load_dotenv
from .telegramBot import main as botMain


class WebterritoriosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webTerritorios'
    def ready(self):
        # Correr Bot de Telegram mientras corra App Django
        with open('logTelegram', "w") as outfile:
            #subprocess.Popen(["python", "webTerritorios/scripts/telegram_bot.py"], stdout=outfile , stderr=subprocess.DEVNULL)
            super().ready()
