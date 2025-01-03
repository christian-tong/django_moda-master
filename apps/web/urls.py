from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import index

app_name='web'
urlpatterns = [
    path('', index, name='index'),

]