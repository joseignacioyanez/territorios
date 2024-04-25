# Generated by Django 5.0.1 on 2024-04-22 14:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webTerritorios', '0007_remove_sordo_genero_id_remove_sordo_senias_tipo_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sordo',
            name='codigo',
            field=models.CharField(blank=True, max_length=10, unique=True),
        ),
        migrations.AddField(
            model_name='sordo',
            name='congregacion',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sordos', to='webTerritorios.congregacion', verbose_name='congregacion'),
        ),
        migrations.AddField(
            model_name='sordo',
            name='local_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='publicador',
            name='nombre',
            field=models.CharField(blank=True, max_length=60),
        ),
        migrations.AlterField(
            model_name='publicador',
            name='telegram_chatid',
            field=models.CharField(blank=True, max_length=15, verbose_name='Telegram Chat ID'),
        ),
        migrations.AlterField(
            model_name='sordo',
            name='detalles_direccion',
            field=models.CharField(blank=True, max_length=400),
        ),
        migrations.AlterField(
            model_name='sordo',
            name='detalles_familia',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='sordo',
            name='detalles_sordo',
            field=models.CharField(blank=True, max_length=400),
        ),
        migrations.AlterField(
            model_name='sordo',
            name='direccion',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='sordo',
            name='telefono',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='sordo',
            name='tipo_senias',
            field=models.CharField(blank=True, max_length=20),
        ),
        migrations.AlterField(
            model_name='territorio',
            name='nombre',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='territorio',
            name='numero',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='Log',
        ),
        migrations.DeleteModel(
            name='TipoLog',
        ),
    ]