# Generated by Django 5.0.1 on 2024-03-22 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webTerritorios', '0002_remove_publicador_email_remove_publicador_nombre_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sordo',
            name='activo',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='asignacion',
            name='fecha_fin',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
