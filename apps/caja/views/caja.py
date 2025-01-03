# views.py
from django.views.generic import ListView,CreateView
from django.views.generic.edit import UpdateView
from django.contrib.auth.decorators import login_required,permission_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from ..models import Caja
from ..forms import CajaForm

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('caja.view_caja', raise_exception=True), name='dispatch')
class CajaListView(ListView):
    model = Caja
    template_name = 'apps/caja/cajas/list.html'  # Nombre de la plantilla

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('caja.add_caja', raise_exception=True), name='dispatch')
class CajaCreateView(CreateView):
    model = Caja
    template_name = 'apps/caja/cajas/add.html'  # Nombre de la plantilla que mostrarás
    form_class = CajaForm
    success_url = reverse_lazy('tesoreria:tesoreria-caja-list')  # Redirige a la lista de cajas después de crear una

@method_decorator(login_required, name='dispatch')
@method_decorator(permission_required('caja.change_caja', raise_exception=True), name='dispatch')
class CajaEditView(UpdateView):
    model = Caja
    template_name = 'apps/caja/cajas/edit.html'  # Nombre de la plantilla que mostrarás
    form_class = CajaForm
    success_url = reverse_lazy('tesoreria:tesoreria-caja-list')  # Redirige a la lista de cajas después de crear una

