# Generated by Django 3.2 on 2023-09-04 09:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("viaje", "0002_alter_programacionasiento_estado"),
    ]

    operations = [
        migrations.AlterField(
            model_name="programacionasiento",
            name="estado",
            field=models.CharField(
                choices=[
                    ("vendido", "Vendido"),
                    ("cortesia", "Cortesía"),
                    ("reservado", "Reservado"),
                    ("libre", "Libre"),
                ],
                default="libre",
                max_length=30,
            ),
        ),
    ]
