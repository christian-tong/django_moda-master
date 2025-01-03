from django.shortcuts import render
from apps.catalogoSunat.models import Ubigeo
from django.db.models import Q
from django.http import JsonResponse

from tablib import Dataset
from .resource import UbigueoResource
 
def importarUbigueo(request):  
    #
    #template = loader.get_template('export/importar.html') 
    print(request.user.is_superuser) 
    if request.method == 'POST' and request.user.is_superuser:  
        persona_resource = UbigueoResource()  
        dataset = Dataset()  
        #print(dataset)  
        nuevas_personas = request.FILES['xlsfile']  
        #print(nuevas_personas)  
        imported_data = dataset.load(nuevas_personas.read())  
        #print(dataset)  
        #result = persona_resource.import_data(dataset, dry_run=True) # Test the data import  #print(result.has_errors())  if not result.has_errors():  
        persona_resource.import_data(dataset, dry_run=False) # Actually import now  return render(request, 'export/importar.html')  

    return render(request,'apps/catalogoSunat/importar.html',{})

def autocomplite(request):
    action = request.GET.get('action',None)
    term = request.GET.get('term',None)
    print(term)

    if action == 'autocomplete' and term is not None:
        data = []
        personas = Ubigeo.objects.filter(
            Q(distrito__icontains=term)|
            Q(provincia__icontains=term)|
            Q(departamento__icontains=term)
            ).distinct()[0:10]
        if personas:
            for i in personas:
                item = i.toJSON()
                item['text'] = i.ubigeo_completo()
                data.append(item)
        else:
            data['error'] = 'No hay datos'
        
        return JsonResponse(data, safe = False)