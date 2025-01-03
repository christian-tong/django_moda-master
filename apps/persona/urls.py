from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import list,add,edit,autocomplite,buscarApiDoc,updateOrdenHappy

app_name='persona'
urlpatterns = [
    path('list/', login_required(list), name='list'),
    path('add/', login_required(add), name='add'),
    path('edit/<int:pk>', login_required(edit), name='edit'),
    path('autocomplite/', login_required(autocomplite), name='autocomplite'),
    path('buscar/api/doc', login_required(buscarApiDoc), name='buscar-api-doc'),
    path('update/orden/happy', login_required(updateOrdenHappy), name='update-orden-happy'),

]