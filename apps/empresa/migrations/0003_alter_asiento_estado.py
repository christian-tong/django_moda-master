# Generated by Django 3.2 on 2024-10-09 17:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("empresa", "0002_alter_asiento_estado"),
    ]

    operations = [
        migrations.AlterField(
            model_name="asiento",
            name="estado",
            field=models.CharField(
                blank=True,
                choices=[
                    ("cortesia", "Cortesía"),
                    ("libre", "Libre"),
                    ("pasadiso", "Pasadiso"),
                ],
                default="libre",
                max_length=20,
                null=True,
            ),
        ),
    ]
