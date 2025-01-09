from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Congregacion(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=60)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id} - {self.nombre}"
    
    class Meta:
        verbose_name = 'Congregación'
        verbose_name_plural = 'Congregaciones'

class EstadoSordo(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombre}"
    
    class Meta:
        verbose_name = 'Estado del Sordo'
        verbose_name_plural = 'Estados de Sordos'

class Territorio(models.Model):
    id = models.AutoField(primary_key=True)
    numero = models.IntegerField(blank=True, null=True)
    nombre = models.CharField(max_length=50, blank=True)
    congregacion = models.ForeignKey(Congregacion, verbose_name="Congregacion", blank=True, null=True, on_delete=models.SET_NULL, related_name="territorios")    
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.congregacion.nombre} - {self.numero} - {self.nombre}"
    
    class Meta:
        verbose_name = 'Territorio'
        verbose_name_plural = 'Territorios'

class Publicador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, related_name="publicador")
    nombre = models.CharField(max_length=60, blank=True)
    activo = models.BooleanField(default=True)
    telegram_chatid = models.CharField(max_length=15, blank=True, verbose_name="Telegram Chat ID")
    congregacion = models.ForeignKey(Congregacion, verbose_name="Congregacion", blank=True, null=True, on_delete=models.SET_NULL, related_name="publicadores")

    def __str__(self):
        return f"{self.id} - {self.nombre} - {self.congregacion.nombre}"

class Sordo(models.Model):
    id = models.AutoField(primary_key=True)
    congregacion = models.ForeignKey(Congregacion, verbose_name="congregacion", blank=True, null=True, on_delete=models.SET_NULL, related_name="sordos")
    local_id = models.IntegerField(blank=True, null=True)
    codigo = models.CharField(max_length=10, unique=True, blank=True)
    nombre = models.CharField(max_length=60, blank=True)
    publicador_estudio = models.ForeignKey(Publicador, verbose_name="Estudia Con", blank=True, null=True, on_delete=models.SET_NULL, related_name="estudiantes")
    tipo_senias = models.CharField(max_length=20, blank=True)
    anio_nacimiento = models.IntegerField(blank=True, null=True)
    telefono = models.CharField(max_length=10, blank=True)
    direccion = models.CharField(max_length=500, blank=True)
    gps_latitud = models.DecimalField(max_digits=11, decimal_places=6, blank=True, null=True)
    gps_longitud = models.DecimalField(max_digits=11, decimal_places=6, blank=True, null=True)
    detalles_sordo = models.CharField(max_length=400, blank=True)
    detalles_familia = models.CharField(max_length=200, blank=True)
    detalles_direccion = models.CharField(max_length=400, blank=True)
    territorio = models.ForeignKey(Territorio, verbose_name="Territorio", blank=True, null=True, on_delete=models.SET_NULL, related_name="sordos")
    estado_sordo = models.ForeignKey(EstadoSordo, verbose_name="Estado del Sordo", blank=True, null=True, on_delete=models.SET_NULL, related_name="sordos_de_este_estado")
    fecha_creacion = models.DateTimeField(auto_now_add=True) #Se crea la fecha de creacion automaticamente
    fecha_ultimo_cambio = models.DateTimeField(auto_now=True) #Se actualiza la fecha de modificacion automaticamente

    def __str__(self):
        nombre = self.nombre if self.nombre else ""
        territorio = str(self.territorio.numero)+' - '+self.territorio.nombre if self.territorio else "❌ Sin Asignar"
        return f"{self.codigo} - {nombre} - {territorio} - {self.estado_sordo}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only for new instances
            # Get the count of existing sordos for this congregacion
            existing_sordos_count = Sordo.objects.filter(congregacion=self.congregacion).count()
            existing_sordos_count += 1
            # Set the local_id for this instance
            self.local_id = existing_sordos_count

        # Generate the code
        initials = "".join(word[0].upper() for word in self.congregacion.nombre.split())
        code = f"{initials}-{self.local_id:03d}"
        self.codigo = code
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("sordo", args=[str(self.id)])
    
class Asignacion(models.Model):
    id = models.AutoField(primary_key=True)
    publicador = models.ForeignKey(Publicador, verbose_name="Publicador", blank=True, null=True, on_delete=models.SET_NULL, related_name="asignaciones_de_este_publicador")
    territorio = models.ForeignKey(Territorio, verbose_name="Territorio", blank=True, null=True, on_delete=models.SET_NULL, related_name="asignaciones_de_este_territorio")
    fecha_asignacion = models.DateField(auto_now_add=True) #Se crea la fecha de creacion automaticamente
    fecha_fin = models.DateField(blank=True, null=True) 

    def __str__(self):
        return f"{self.id} - {self.territorio.nombre} - {self.publicador.nombre} - {self.fecha_asignacion} - {self.fecha_fin}"
    
    class Meta:
        verbose_name = 'Asignación'
        verbose_name_plural = 'Asignaciones'