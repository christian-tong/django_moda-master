# Generated by Django 3.2 on 2024-10-10 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viaje', '0008_alter_programacionasiento_estado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programacionasiento',
            name='estado',
            field=models.CharField(choices=[('libre', 'Libre'), ('reservado', 'Reservado'), ('cortesia', 'Cortesía'), ('vendido', 'Vendido')], default='libre', max_length=30),
        ),
    ]
