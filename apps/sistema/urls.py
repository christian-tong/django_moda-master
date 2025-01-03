from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import (userAdd,userList,accountLogin,accountLoggout,menuList,userAgencia,
                    homeIndex)

app_name='sistema'
urlpatterns = [
    path('user/add', login_required(userAdd), name='user-add'),
    path('user/list', login_required(userList), name='user-list'),
    path('user/agencia/list', login_required(userAgencia), name='user-agencia-list'),
    path('account/login', accountLogin, name='account-login'),
    path('account/loggout', login_required(accountLoggout), name='account-loggout'),
    path('menu/list', login_required(menuList), name='menu-list'),
    path('', login_required(homeIndex), name='home-index'),

]