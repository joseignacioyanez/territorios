from . import views
from django.urls import path

app_name = "webTerritorios"
urlpatterns = [
    path("menu/", views.MenuView.as_view(), name="menu"),
    path("asignar/", views.AsignarView.as_view(), name="asignar"),
    path("usuario/", views.datos_usuario_view, name="datos_usuario"),
    path("publicadores/", views.publicadores_activos_misma_congregacion_view, name="publicadores"),
    path("usuario_telegram/", views.get_usuario_por_chatid_view, name="usuario_telegram"),
    path("asignacion_pendiente/", views.verificar_asignacion_pendiente, name="asignacion_pendiente"),
    path("territorios_disponibles/", views.territorios_disponibles, name="territorios_disponibles"),
]
