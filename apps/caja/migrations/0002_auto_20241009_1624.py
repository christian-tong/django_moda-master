# Generated by Django 3.2 on 2024-10-09 21:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("caja", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="caja",
            name="montoEntrada",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name="caja",
            name="montoSalida",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name="caja",
            name="saldo",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
