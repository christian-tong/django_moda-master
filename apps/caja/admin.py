from django.contrib import admin
from .models import TipoMovimiento,TipoMedioPago,Caja,MovimientoCaja,MedioPago,CierreCajaMes

@admin.register(TipoMovimiento)
class Admin(admin.ModelAdmin):
    list_display =  [f.name for f in TipoMovimiento._meta.fields]

@admin.register(TipoMedioPago)
class Admin(admin.ModelAdmin):
    list_display =  [f.name for f in TipoMedioPago._meta.fields]

@admin.register(Caja)
class Admin(admin.ModelAdmin):
    list_display =  [f.name for f in Caja._meta.fields]
    autocomplete_fields = ['cajeros',]

@admin.register(MovimientoCaja)
class Admin(admin.ModelAdmin):
    list_display =  [f.name for f in MovimientoCaja._meta.fields]

@admin.register(MedioPago)
class Admin(admin.ModelAdmin):
    list_display =  [f.name for f in MedioPago._meta.fields]

@admin.register(CierreCajaMes)
class Admin(admin.ModelAdmin):
    list_display =  [f.name for f in CierreCajaMes._meta.fields]
