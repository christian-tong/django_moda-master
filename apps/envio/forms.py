from django import forms

from apps.persona.models import Persona
from apps.empresa.models import Agencia
from .models import Encomienda,Liquidacion,liquidacionRecepcion,ClienteRecepcion

class EncomiendaForm(forms.ModelForm):
    remite = forms.ModelChoiceField(queryset=Persona.objects.filter(numDoc='44319644'))
    consignado = forms.ModelChoiceField(queryset=Persona.objects.filter(numDoc='44319644'))
    class Meta:
        model = Encomienda
        fields = '__all__'

        labels = {
            'seguridadClave': 'Clave de 4 digitos'
        }
        widgets = {
            'agenciaOrigen': forms.Select(attrs={'class':'select'}),
            'agenciaDestino': forms.Select(attrs={'class':'select'}),
            'seguridadClave':forms.PasswordInput()
        }

    def clean_agenciaDestino(self):
        agenciaDestino = self.cleaned_data.get('agenciaDestino',None)
        agenciaOrigen = self.cleaned_data.get('agenciaOrigen',None)
        
        if agenciaOrigen is not None and agenciaDestino is not None:
            if agenciaOrigen == agenciaDestino:
                raise forms.ValidationError('La agencia destino no debe ser igual a la agencia origen..!!')
        return agenciaDestino


class LiquidacionForm(forms.ModelForm):
    class Meta:
        model = Liquidacion
        #fields = '__all__'
        exclude = ['encomienda',]

class liquidacionRecepcionForm(forms.ModelForm):

    class Meta:
        model = liquidacionRecepcion
        fields = '__all__'


class ClienteRecepcionForm(forms.ModelForm):
    clave = forms.CharField(label='Clave de seguridad')

    class Meta:
        model = ClienteRecepcion
        fields = '__all__'