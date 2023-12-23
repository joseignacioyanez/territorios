from . import views
from django.urls import path

app_name = "webTerritorios"
urlpatterns = [
    path("", views.index, name="index"),
    path("addSordo", views.addSordo, name="addSordo"),
    path("editSordo/<int:id>", views.editSordo, name="editSordo"),
    path("deleteSordo/<int:id>", views.deleteSordo, name="deleteSordo")
]
