from django import forms

from apps.persona.models import Persona,PersonaNatural


class PersonaForm(forms.ModelForm):
    #fechaNac = forms.CharField(label="Fecha de nacimiento",required=False,widget=forms.TextInput(attrs={'class': 'datepicker'}))
  
    class Meta:
        model = Persona
        fields = '__all__'

    
    def clean_fechaNac(self):
        fechanac = self.cleaned_data.get('fechaNac')
        if not fechanac:
            fechanac=None
        return fechanac
        
    def clean_numDoc(self):
        tipodoc = self.cleaned_data.get('tipoDoc')
        numdoc = len(str(self.cleaned_data.get('numDoc')))
        
        if tipodoc != None:
            
            if tipodoc.codigo == '6' and numdoc != 11:
                print('ruc')
                raise forms.ValidationError('El RUC tiene que tener 11 dígitos')
            elif tipodoc.codigo == '1' and numdoc != 8:
                print('dni')
                raise forms.ValidationError('El DNI tiene que tener 8 dígitos')        
            else:
                pass
        return self.cleaned_data.get('numDoc')

class PersonaNaturalForm(forms.ModelForm):

    class Meta:
        model = PersonaNatural
        exclude = ('persona',)

        widgets ={
            'fechaNac': forms.DateInput(attrs={'type': 'date'})
        }


