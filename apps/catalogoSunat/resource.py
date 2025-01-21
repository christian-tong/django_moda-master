from import_export import resources
from .models import Ubigeo


class UbigueoResource(resources.ModelResource):
    class Meta:
        model = Ubigeo
