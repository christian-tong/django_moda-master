from django.shortcuts import render
from apps.empresa.models import Agencia


# Create your views here.
def index(request):
    agencias = Agencia.objects.all()
    context = {agencias: agencias}
    return render(request, "apps/web/index.html", context)
