from django.contrib import admin
from .models import Encomienda,Liquidacion,liquidacionRecepcion,ClienteRecepcion

    


@admin.register(Encomienda)
class Admin(admin.ModelAdmin):
    list_display =  [f.name for f in Encomienda._meta.fields]
    search_fields = ['remite__denominacion','consignado__denominacion']
    autocomplete_fields = ['remite','consignado']
    #list_filter = ['remite','consignado']

@admin.register(Liquidacion)
class Admin(admin.ModelAdmin):
    list_display =  [f.name for f in Liquidacion._meta.fields]

@admin.register(liquidacionRecepcion)
class Admin(admin.ModelAdmin):
    list_display =  [f.name for f in liquidacionRecepcion._meta.fields]

@admin.register(ClienteRecepcion)
class Admin(admin.ModelAdmin):
    list_display =  [f.name for f in ClienteRecepcion._meta.fields]
