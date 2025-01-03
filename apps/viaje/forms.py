from django import forms
from .models import Embarque,ProgramacionViaje,ProgramacionAsiento,Manifiesto
from apps.persona.models import Persona

class EmbarqueForm(forms.ModelForm):
    idprograma = forms.CharField()
    idasiento= forms.CharField(widget= forms.HiddenInput())
    pasajero = forms.ModelChoiceField(queryset=Persona.objects.filter(numDoc='44319644'), empty_label="Select an author")

    class Meta:
        model = Embarque
        fields = '__all__'

        labels = {
            'programacionViaje':'Ruta'
        }

        widgets = {
            'numAsiento': forms.TextInput(attrs={'readonly':True,'value':'0','class':'estetica'}),
            'precio': forms.NumberInput(attrs={'class':'estetica'}),
            'lugar_abordo': forms.Select(attrs={'class':'select'}),
            'lugar_bajada': forms.Select(attrs={'class':'select'}),
            'hora_abordo': forms.DateTimeInput(attrs={'type': 'time'})
        }
    
    def clean_numAsiento(self):
        numAsiento = self.cleaned_data.get('numAsiento')

        
        if numAsiento == '0':
            raise forms.ValidationError('Tienes que elegir un numero de asiento')
        return numAsiento

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        
        if precio <= 0:

            raise forms.ValidationError('Ingrese un precio adecuado')
        return precio

    def clean_idasiento(self):
        idasiento = int(self.cleaned_data.get('idasiento'))
        asiento = ProgramacionAsiento.objects.get(id=idasiento, estado='libre')
        
        if not asiento:
            raise forms.ValidationError('El asiento ya esta ocupado, seleccione otro!')
        return idasiento

class EmbarqueEditForm(forms.ModelForm):

    class Meta:
        model = Embarque
        #fields = '__all__'
        exclude = ['numDocumento','venta','precio','pasajero']
        widgets = {
            'numAsiento': forms.TextInput(attrs={'readonly':True,'value':'0','class':'estetica'}),
            'hora_abordo': forms.DateTimeInput(attrs={'type': 'time'})
        }

class ProgramacionViajeForm(forms.ModelForm):

    class Meta:
        model = ProgramacionViaje
        fields = '__all__'

        labels = {
            'fechaViaje':'Fecha de viaje'
        }

        widgets = {
            'fechaViaje': forms.DateInput(attrs={'type': 'date'}),
            'horaViaje': forms.DateTimeInput(attrs={'type': 'time'})
        }

class BuscarViajeForm(forms.ModelForm):

    class Meta:
        model = ProgramacionViaje
        fields = ('rutaOrigen','rutaDestino','fechaViaje','activo')

        widgets={
            'fechaViaje': forms.DateInput(attrs={'type':'date'})
        }

class ManifiestoForm(forms.ModelForm):

    class Meta:
        model = Manifiesto
        exclude = ['numDocumento','programacionViaje',]

        widgets={
            'fechaViaje': forms.DateInput(attrs={'type':'date'})
        }


class ProgramacionAsientoForm(forms.ModelForm):
    idasiento = forms.CharField(required=False)

    class Meta:
        model = ProgramacionAsiento
        fields = '__all__'
