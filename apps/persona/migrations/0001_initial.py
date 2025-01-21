# Generated by Django 3.2 on 2022-10-22 20:21

import apps.persona.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("catalogoSunat", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Persona",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "numDoc",
                    models.CharField(
                        max_length=11, unique=True, verbose_name="Numero Documento"
                    ),
                ),
                (
                    "denominacion",
                    models.CharField(
                        blank=True,
                        max_length=150,
                        null=True,
                        verbose_name="Razón Social/Nombre y Apellidos",
                    ),
                ),
                (
                    "direccion",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Dirección"
                    ),
                ),
                (
                    "fijo",
                    models.CharField(
                        blank=True,
                        max_length=10,
                        null=True,
                        verbose_name="Teléfono fijo",
                    ),
                ),
                (
                    "movilUno",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="Celular"
                    ),
                ),
                (
                    "movilDos",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="Celular2"
                    ),
                ),
                (
                    "correo",
                    models.EmailField(
                        blank=True, max_length=250, null=True, verbose_name="Correo"
                    ),
                ),
                ("activo", models.BooleanField(default=True)),
                (
                    "tipoDoc",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="catalogoSunat.tipodocumentoidentidad",
                        verbose_name="Tipo de Documento",
                    ),
                ),
                (
                    "ubigueo",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="catalogoSunat.ubigeo",
                    ),
                ),
            ],
            options={
                "verbose_name": "Persona",
                "verbose_name_plural": "Personas",
            },
        ),
        migrations.CreateModel(
            name="PersonaNatural",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nombres", models.CharField(max_length=100)),
                ("apellidoP", models.CharField(max_length=100)),
                ("apellidoM", models.CharField(max_length=100)),
                (
                    "fechaNac",
                    models.DateField(
                        blank=True, null=True, verbose_name="Fecha de Nacimiento"
                    ),
                ),
                (
                    "foto",
                    models.ImageField(
                        blank=True,
                        default="persona/default.png",
                        upload_to=apps.persona.models.rutaNombreImagen,
                        verbose_name="Foto",
                    ),
                ),
                (
                    "genero",
                    models.CharField(
                        blank=True,
                        choices=[("F", "Femenino"), ("M", "Masculino")],
                        max_length=10,
                        null=True,
                        verbose_name="Género",
                    ),
                ),
                ("ordenhappy", models.SmallIntegerField(blank=True, null=True)),
                (
                    "persona",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="persona.persona",
                    ),
                ),
            ],
            options={
                "verbose_name": "PersonaNatural",
                "verbose_name_plural": "PersonaNaturals",
            },
        ),
        migrations.CreateModel(
            name="PersonaJuridica",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("estado", models.BooleanField(blank=True, default=True, null=True)),
                ("condicion", models.CharField(blank=True, max_length=20, null=True)),
                (
                    "persona",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="persona.persona",
                    ),
                ),
            ],
            options={
                "verbose_name": "PersonaJuridica",
                "verbose_name_plural": "PersonaJuridicas",
            },
        ),
    ]
