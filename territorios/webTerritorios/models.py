from django.db import models
from django.urls import reverse

class Sordo(models.Model):
    name = models.CharField(max_length=64)
    direccion = models.CharField(max_length=256)
    edad = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.direccion} - {self.edad}"

    def get_absolute_url(self):
        return reverse("webTerritorios:index")