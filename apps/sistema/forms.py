from django import forms
from django.forms import widgets
from .models import Usuario



class UsuarioForm(forms.ModelForm):
    password1 = forms.CharField(label='Repita contraseña')
    class Meta:
        model = Usuario
        fields = '__all__'
        exclude =('date_joined',)

        labels = {
            'groups':'Roles',
            'is_superuser':'Es super user',
        }
    
    def clean_password1(self):
        pws = self.cleaned_data.get('password')
        pws1 = self.cleaned_data.get('password1')

        if pws != pws1 or pws1 is None :
            raise forms.ValidationError('Contraseña no son iguales') 
        return pws1


class UsuarioLoginForm(forms.Form):
    username = forms.CharField(label='Usuario')
    password = forms.CharField(label='Contraseña',widget=forms.PasswordInput())

class UsuarioAgenciaForm(forms.Form):
    agencia = forms.ModelChoiceField(queryset=Usuario.objects.none(),
    widget=forms.RadioSelect)

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        if request:
            listdata = self.fields['agencia']
            listdata.queryset = Usuario.objects.get(id=request.user.id).agencia.all()