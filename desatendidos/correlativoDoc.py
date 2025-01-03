from apps.empresa.models import AgenciaDocumento
def incrementa(request, cod_doc):
    if request.session['agencia_id']:
        correlativoAgeUpd = AgenciaDocumento.objects.get(
            agencia=request.user.agencia.get(id=request.session['agencia_id']),
            documento__codigo=cod_doc)

    return {'serie': correlativoAgeUpd.serie, 'correlativo':correlativoAgeUpd.correlativoMas()}