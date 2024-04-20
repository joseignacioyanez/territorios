import subprocess
from django.apps import AppConfig
from .telegramBot import main as botMain


class WebterritoriosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'webTerritorios'
    def ready(self):
        # Correr Bot de Telegram mientras corra App Django
        #subprocess.Popen(["python", "webTerritorios/telegramBot.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        super().ready()
