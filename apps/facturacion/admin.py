from django.contrib import admin
from .models import FaturaBoleta

@admin.register(FaturaBoleta)
class Admin(admin.ModelAdmin):
    list_display =  [f.name for f in FaturaBoleta._meta.fields]
