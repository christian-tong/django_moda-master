from django.contrib import admin

from apps.sistema.models import Usuario,Menu


@admin.register(Usuario)
class Admin(admin.ModelAdmin):

    list_display =  [f.name for f in Usuario._meta.fields]
    autocomplete_fields = ['persona',]

    
@admin.register(Menu)
class Admin(admin.ModelAdmin):

    list_display =  [f.name for f in Menu._meta.fields]
