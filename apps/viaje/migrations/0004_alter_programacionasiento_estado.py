# Generated by Django 3.2 on 2024-10-09 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viaje', '0003_alter_programacionasiento_estado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programacionasiento',
            name='estado',
            field=models.CharField(choices=[('reservado', 'Reservado'), ('cortesia', 'Cortesía'), ('vendido', 'Vendido'), ('libre', 'Libre')], default='libre', max_length=30),
        ),
    ]
