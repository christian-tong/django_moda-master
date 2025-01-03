from django.forms.models import model_to_dict

def toJSON(obj,exclude=[]):
    if obj:
        return model_to_dict(obj,exclude=exclude)
    else: return 'El objeto esta vacio'
