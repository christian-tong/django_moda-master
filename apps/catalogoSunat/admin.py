from django.contrib import admin
from .models import TipoDocumento, TipoDocumentoIdentidad, Ubigeo


@admin.register(TipoDocumento)
class Admin(admin.ModelAdmin):
    list_display = [f.name for f in TipoDocumento._meta.fields]


@admin.register(TipoDocumentoIdentidad)
class Admin(admin.ModelAdmin):
    list_display = [f.name for f in TipoDocumentoIdentidad._meta.fields]


@admin.register(Ubigeo)
class Admin(admin.ModelAdmin):
    list_display = [f.name for f in Ubigeo._meta.fields]
    search_fields = ("distrito",)
