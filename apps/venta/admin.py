from django.contrib import admin
from .models import Movimiento, DetalleMov


@admin.register(Movimiento)
class Admin(admin.ModelAdmin):
    list_display = [f.name for f in Movimiento._meta.fields]


@admin.register(DetalleMov)
class Admin(admin.ModelAdmin):
    list_display = [f.name for f in DetalleMov._meta.fields]
