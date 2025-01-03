from django.contrib import admin
from apps.persona.models import Persona, PersonaJuridica, PersonaNatural

@admin.register(Persona)
class Admin(admin.ModelAdmin):
    list_display =  [f.name for f in Persona._meta.fields]
    search_fields = ('denominacion','numDoc')
    autocomplete_fields = ['ubigueo',]
    """list_filter = ('',)
    raw_id_fields = ('',)    
    
    date_hierarchy = ''
    ordering = ('',)"""

@admin.register(PersonaNatural)
class Admin(admin.ModelAdmin):
    list_display =  [f.name for f in PersonaNatural._meta.fields]

@admin.register(PersonaJuridica)
class Admin(admin.ModelAdmin):
    list_display =  [f.name for f in PersonaJuridica._meta.fields]
