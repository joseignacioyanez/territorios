from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User



class Congregacion(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=60)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id} - {self.nombre}"

class Genero(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombre}"
    
    class Meta:
        verbose_name = 'Género'
        verbose_name_plural = 'Géneros'

class SeniasTipo(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombre}"
    
    class Meta:
        verbose_name = 'Tipo de Señas'
        verbose_name_plural = 'Tipos de Señas'

class EstadoSordo(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.id} - {self.nombre}"
    
    class Meta:
        verbose_name = 'Estado del Sordo'
        verbose_name_plural = 'Estados de Sordos'

class Territorio(models.Model):
    id = models.AutoField(primary_key=True)
    numero = models.IntegerField()
    nombre = models.CharField(max_length=50)
    congregacion = models.ForeignKey(Congregacion, verbose_name="Congregacion", blank=True, null=True, on_delete=models.SET_NULL, related_name="territorios")    
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id} - {self.numero} {self.congregacion.nombre} - {self.nombre}"
    
    class Meta:
        verbose_name = 'Territorio'
        verbose_name_plural = 'Territorios'

class Publicador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    nombre = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, blank=True, null=True)
    telefono = models.CharField(max_length=10, blank=True, null=True)
    activo = models.BooleanField(default=True)
    telegram_chatid = models.CharField(max_length=15, blank=True, null=True, verbose_name="Telegram Chat ID")
    congregacion = models.ForeignKey(Congregacion, verbose_name="Congregacion", blank=True, null=True, on_delete=models.SET_NULL, related_name="publicadores")

    def __str__(self):
        return f"{self.id} - {self.nombre} - {self.congregacion.nombre}"

class Sordo(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=5)
    nombre = models.CharField(max_length=50)
    publicador_estudio = models.ForeignKey(Publicador, verbose_name="Estudia Con", blank=True, null=True, on_delete=models.SET_NULL, related_name="estudiantes")
    genero_id = models.ForeignKey(Genero, verbose_name="Genero", blank=True, null=True, on_delete=models.SET_NULL, related_name="sordos_de_este_genero")
    senias_tipo = models.ForeignKey(SeniasTipo, verbose_name="Tipo de Señas", blank=True, null=True, on_delete=models.SET_NULL, related_name="sordos_de_este_tipo")
    anio_nacimiento = models.IntegerField(blank=True, null=True)
    telefono = models.CharField(max_length=10, blank=True, null=True)
    direccion = models.CharField(max_length=500, blank=True, null=True)
    gps_latitud = models.DecimalField(max_digits=11, decimal_places=6, blank=True, null=True)
    gps_longitud = models.DecimalField(max_digits=11, decimal_places=6, blank=True, null=True)
    descripcion = models.CharField(max_length=500, blank=True, null=True)
    territorio = models.ForeignKey(Territorio, verbose_name="Territorio", blank=True, null=True, on_delete=models.SET_NULL, related_name="sordos")
    estado_sordo = models.ForeignKey(EstadoSordo, verbose_name="Estado del Sordo", blank=True, null=True, on_delete=models.SET_NULL, related_name="sordos_de_este_estado")
    fecha_creacion = models.DateTimeField(auto_now_add=True) #Se crea la fecha de creacion automaticamente
    fecha_ultimo_cambio = models.DateTimeField(auto_now=True) #Se actualiza la fecha de modificacion automaticamente

    def __str__(self):
        return f"{self.codigo} - {self.territorio.nombre} - {self.nombre} - {self.estado_sordo}"
    
    def get_absolute_url(self):
        return reverse("sordo", args=[str(self.id)])

class TipoLog(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.id} - {self.nombre}"
    
    class Meta:
        verbose_name = 'Tipo de Log'
        verbose_name_plural = 'Tipos de Log'

class Log(models.Model):
    id = models.AutoField(primary_key=True)
    tipo_log = models.ForeignKey(TipoLog, verbose_name="Tipo de Log", blank=True, null=True, on_delete=models.SET_NULL, related_name="logs_de_este_tipo")
    publicador = models.ForeignKey(Publicador, verbose_name="Publicador", blank=True, null=True, on_delete=models.SET_NULL, related_name="logs_de_este_publicador")
    detalle = models.CharField(max_length=200, blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True) #Se crea la fecha de creacion automaticamente

    def __str__(self):
        return f"{self.id} - {self.fecha} - {self.detalle}"
    
class Asignacion(models.Model):
    id = models.AutoField(primary_key=True)
    publicador = models.ForeignKey(Publicador, verbose_name="Publicador", blank=True, null=True, on_delete=models.SET_NULL, related_name="asignaciones_de_este_publicador")
    territorio = models.ForeignKey(Territorio, verbose_name="Territorio", blank=True, null=True, on_delete=models.SET_NULL, related_name="asignaciones_de_este_territorio")
    fecha_asignacion = models.DateTimeField(auto_now_add=True) #Se crea la fecha de creacion automaticamente
    fecha_fin = models.DateTimeField(auto_now=True, blank=True, null=True) 

    def __str__(self):
        return f"{self.id} - {self.territorio.nombre} - {self.publicador.nombre} - {self.fecha_asignacion}"
    
    class Meta:
        verbose_name = 'Asignación'
        verbose_name_plural = 'Asignaciones'