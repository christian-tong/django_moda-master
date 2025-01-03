from django.urls import path
from django.contrib.auth.decorators import login_required
from .views.movimiento import movimiento_add
from .views.caja import CajaListView,CajaCreateView,CajaEditView

app_name='tesoreria'
urlpatterns = [
    path('movimiento/add', movimiento_add, name='tesoreria-movimiento-add'),
    path('caja/add', CajaCreateView.as_view(), name='tesoreria-caja-add'),
    path('caja/list', CajaListView.as_view(), name='tesoreria-caja-list'),
    path('caja/edit/<int:pk>', CajaEditView.as_view(), name='tesoreria-caja-edit'),

]