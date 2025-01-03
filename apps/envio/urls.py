from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import (encomiendaAdd,encomiendaList,liquidacionList,liquidacionAdd,
                    liquidacionAddEncomienda,liquidacionPrint,liquidacionEdit,                    
                    liquidacionSacarEncomienda,liquidacionRecepcion,
                    liquidacionFinalizar,encomiendaRecepcion,encomiendaPrintA5)
from .views import encomiendaPrint
app_name='envio'
urlpatterns = [
    path('encomienda/add/', login_required(encomiendaAdd), name='encomienda-add'),
    path('encomienda/list/', login_required(encomiendaList), name='encomienda-list'),
    path('encomienda/recepcion/', login_required(encomiendaRecepcion), name='encomienda-recepcion'),
    path('encomienda/print/', login_required(encomiendaPrint), name='encomienda-print'),
    path('encomienda/print/A5/<int:encom_pk>/', login_required(encomiendaPrintA5), name='encomienda-print-a5'),
    path('liquidacion/add/', login_required(liquidacionAdd), name='liquidacion-add'),
    path('liquidacion/list/', login_required(liquidacionList), name='liquidacion-list'),
    path('liquidacion/edit/', login_required(liquidacionEdit), name='liquidacion-edit'),
    path('liquidacion/add/encomienda/', login_required(liquidacionAddEncomienda), name='liquidacion-add-encomienda'),
    path('liquidacion/sacar/encomienda/', login_required(liquidacionSacarEncomienda), name='liquidacion-sacar-encomienda'),
    path('liquidacion/finalizar/', login_required(liquidacionFinalizar), name='liquidacion-finalizar'),
    path('liquidacion/recepcion/', login_required(liquidacionRecepcion), name='liquidacion-recepcion'),
    path('liquidacion/print/', login_required(liquidacionPrint), name='liquidacion-print'),
]