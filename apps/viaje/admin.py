from django.contrib import admin

from .models import Embarque,ProgramacionViaje,Manifiesto,ProgramacionAsiento

@admin.register(Embarque)
class Admin(admin.ModelAdmin):
    list_display =  [f.name for f in Embarque._meta.fields]

@admin.register(ProgramacionViaje)
class Admin(admin.ModelAdmin):
    list_display =  [f.name for f in ProgramacionViaje._meta.fields]

@admin.register(Manifiesto)
class Admin(admin.ModelAdmin):
    list_display =  [f.name for f in Manifiesto._meta.fields]


@admin.register(ProgramacionAsiento)
class Admin(admin.ModelAdmin):
    list_display =  [f.name for f in ProgramacionAsiento._meta.fields]
