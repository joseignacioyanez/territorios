from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('webTerritorios', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asignacion',
            name='fecha_asignacion',
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='asignacion',
            name='fecha_fin',
            field=models.DateField(blank=True, null=True),
        ),
    ]