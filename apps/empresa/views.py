from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView
from apps.empresa.forms import ConductorForm, AgenciaForm
from apps.empresa.models import Agencia, Conductor


class ConductorList(ListView):
    model = Conductor
    paginate_by = 10
    context_object_name = "entity"
    template_name = "apps/empresa/conductor/list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", None)
        if q:
            qs = qs.filter(
                Q(chofer__denominacion__icontains=q) | Q(chofer__numDoc__icontains=q)
            ).distinct()

        return qs


class ConductorAdd(CreateView):
    model = Conductor
    form_class = ConductorForm
    success_url = reverse_lazy("empresa:conductor-list")
    template_name = "apps/empresa/conductor/add.html"


class ConductorUpdate(UpdateView):
    model = Conductor
    form_class = ConductorForm
    success_url = reverse_lazy("empresa:conductor-list")
    template_name = "apps/empresa/conductor/add.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data["form"] = self.form_class(self.request.POST, instance=self.object)
        else:
            self.object = self.get_object()
            self.object.fechaExpedicion = (
                self.object.fechaExpedicion.isoformat()
                if self.object.fechaExpedicion
                else self.object.fechaExpedicion
            )
            self.object.fechaRevalidacion = (
                self.object.fechaRevalidacion.isoformat()
                if self.object.fechaRevalidacion
                else self.object.fechaRevalidacion
            )
            data["form"] = self.form_class(instance=self.object)
        return data


class AgenciaList(ListView):
    model = Agencia
    paginate_by = 10
    context_object_name = "entity"
    template_name = "apps/empresa/agencia/list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", None)
        if q:
            qs = qs.filter(nombre=q).distinct()

        return qs


class AgenciaAdd(CreateView):
    model = Agencia
    form_class = AgenciaForm
    success_url = reverse_lazy("empresa:agencia-list")
    template_name = "apps/empresa/agencia/add.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.empresa = Agencia.objects.filter(tipo="PRINCIPAL").first().empresa
        self.object.tipo = "SUCURSAL"
        return super().form_valid(form)


class AgenciaUpdate(UpdateView):
    model = Agencia
    form_class = AgenciaForm
    success_url = reverse_lazy("empresa:agencia-list")
    template_name = "apps/empresa/agencia/add.html"
