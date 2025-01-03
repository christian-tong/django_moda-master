from django import forms
from django.forms import widgets

from .models import DetalleMov

class DetalleMovForm(forms.ModelForm):

    class Meta:
        model = DetalleMov
        fields = '__all__'

        """labels = {
            'subTotal' :'Total'
        }
        """
        widgets = {
            'unidadMedida': forms.Select(attrs={'class':'select'}),
        }
    
    