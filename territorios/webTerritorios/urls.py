from . import views
from django.urls import path

app_name = "webTerritorios"
urlpatterns = [
    path("menu/", views.MenuView.as_view(), name="menu"),
    path("asignar/", views.AsignarView.as_view(), name="asignar"),
]
