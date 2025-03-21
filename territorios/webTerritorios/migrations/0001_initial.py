# Generated by Django 5.0.1 on 2025-01-09 14:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Congregacion',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=60)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Congregación',
                'verbose_name_plural': 'Congregaciones',
            },
        ),
        migrations.CreateModel(
            name='EstadoSordo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=20)),
            ],
            options={
                'verbose_name': 'Estado del Sordo',
                'verbose_name_plural': 'Estados de Sordos',
            },
        ),
        migrations.CreateModel(
            name='Publicador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(blank=True, max_length=60)),
                ('activo', models.BooleanField(default=True)),
                ('telegram_chatid', models.CharField(blank=True, max_length=15, verbose_name='Telegram Chat ID')),
                ('congregacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='publicadores', to='webTerritorios.congregacion', verbose_name='Congregacion')),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='publicador', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Territorio',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('numero', models.IntegerField(blank=True, null=True)),
                ('nombre', models.CharField(blank=True, max_length=50)),
                ('activo', models.BooleanField(default=True)),
                ('congregacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='territorios', to='webTerritorios.congregacion', verbose_name='Congregacion')),
            ],
            options={
                'verbose_name': 'Territorio',
                'verbose_name_plural': 'Territorios',
            },
        ),
        migrations.CreateModel(
            name='Sordo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('local_id', models.IntegerField(blank=True, null=True)),
                ('codigo', models.CharField(blank=True, max_length=10, unique=True)),
                ('nombre', models.CharField(blank=True, max_length=60)),
                ('tipo_senias', models.CharField(blank=True, max_length=20)),
                ('anio_nacimiento', models.IntegerField(blank=True, null=True)),
                ('telefono', models.CharField(blank=True, max_length=10)),
                ('direccion', models.CharField(blank=True, max_length=500)),
                ('gps_latitud', models.DecimalField(blank=True, decimal_places=6, max_digits=11, null=True)),
                ('gps_longitud', models.DecimalField(blank=True, decimal_places=6, max_digits=11, null=True)),
                ('detalles_sordo', models.CharField(blank=True, max_length=400)),
                ('detalles_familia', models.CharField(blank=True, max_length=200)),
                ('detalles_direccion', models.CharField(blank=True, max_length=400)),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('fecha_ultimo_cambio', models.DateTimeField(auto_now=True)),
                ('congregacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sordos', to='webTerritorios.congregacion', verbose_name='congregacion')),
                ('estado_sordo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sordos_de_este_estado', to='webTerritorios.estadosordo', verbose_name='Estado del Sordo')),
                ('publicador_estudio', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='estudiantes', to='webTerritorios.publicador', verbose_name='Estudia Con')),
                ('territorio', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sordos', to='webTerritorios.territorio', verbose_name='Territorio')),
            ],
        ),
        migrations.CreateModel(
            name='Asignacion',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_asignacion', models.DateField(auto_now_add=True)),
                ('fecha_fin', models.DateField(blank=True, null=True)),
                ('publicador', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='asignaciones_de_este_publicador', to='webTerritorios.publicador', verbose_name='Publicador')),
                ('territorio', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='asignaciones_de_este_territorio', to='webTerritorios.territorio', verbose_name='Territorio')),
            ],
            options={
                'verbose_name': 'Asignación',
                'verbose_name_plural': 'Asignaciones',
            },
        ),
    ]
