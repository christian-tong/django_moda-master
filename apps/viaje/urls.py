from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import (embarqueAdd,embarqueList,embarqueEdit,programa_add,manifiestoEdit,
                    programaEdit,programaList,programaAsientoEdit,programaAsientoList,
                    manifiestoPrint,embarqueCambiar,embarquePrint)
                    
app_name='viaje'
urlpatterns = [
    path('embarque/add/', login_required(embarqueAdd), name='embarque-add'),
    path('embarque/list/', login_required(embarqueList), name='embarque-list'),
    path('embarque/edit/', login_required(embarqueEdit), name='embarque-edit'),
    path('embarque/cambiar/', login_required(embarqueCambiar), name='embarque-cambiar'),
    path('embarque/print/', login_required(embarquePrint), name='embarque-print'),
    path('programa/list/', login_required(programaList), name='programa-list'),
    path('programa/add/', login_required(programa_add), name='programa-add'),
    path('programa/edit/', login_required(programaEdit), name='programa-edit'),
    path('programa/asiento/edit/', login_required(programaAsientoEdit), name='programa-asiento-edit'),
    path('programa/asiento/list/', login_required(programaAsientoList), name='programa-asiento-list'),
    path('manifiesto/edit/', login_required(manifiestoEdit), name='manifiesto-edit'),
    path('manifiesto/print/', login_required(manifiestoPrint), name='manifiesto-print'),
    

]