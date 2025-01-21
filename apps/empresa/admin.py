from django.contrib import admin
from .models import Agencia, AgenciaDocumento, Vehiculo, Conductor, Asiento


@admin.register(Agencia)
class Admin(admin.ModelAdmin):
    list_display = [f.name for f in Agencia._meta.fields]
    autocomplete_fields = ["ubigeo", "responsable", "empresa"]


@admin.register(AgenciaDocumento)
class Admin(admin.ModelAdmin):
    list_display = [f.name for f in AgenciaDocumento._meta.fields]


@admin.register(Vehiculo)
class Admin(admin.ModelAdmin):
    list_display = [f.name for f in Vehiculo._meta.fields]
    search_fields = ("placa",)


@admin.register(Asiento)
class Admin(admin.ModelAdmin):
    list_display = [f.name for f in Asiento._meta.fields]


@admin.register(Conductor)
class Admin(admin.ModelAdmin):
    list_display = [f.name for f in Conductor._meta.fields]
    autocomplete_fields = [
        "chofer",
    ]
    search_fields = ["chofer__denominacion", "numLicencia"]
