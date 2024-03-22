from . import views
from django.urls import path

app_name = "webTerritorios"
urlpatterns = [
    path("menu", views.menu, name="menu"),
    path("asignar", views.asignar, name="asignar")
]
