from django import forms
from .models import FaturaBoleta
from apps.catalogoSunat.models import TipoDocumento
from apps.persona.models import Persona


class FacturaBoletaForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(queryset=Persona.objects.all())

    class Meta:
        model = FaturaBoleta
        fields = "__all__"

        widgets = {
            "tipoDocumento": forms.Select(attrs={"class": "select"}),
            "cliente": forms.Select(attrs={"class": "select"}),
        }

    def clean(self):
        cleaned_data = super(FacturaBoletaForm, self).clean()

        tdoc = cleaned_data.get("tipoDocumento", None)
        clie = cleaned_data.get("cliente", None)
        if tdoc is not None and clie is not None:
            if tdoc.codigo == "01" and clie.tipoDoc.codigo != "6":
                self.add_error("cliente", "El Cliente debe ser persona juridica")
                # raise forms.ValidationError('El Cliente debe ser persona juridica')
            elif tdoc.codigo == "03" and clie.tipoDoc.codigo != "1":
                self.add_error("cliente", "El Cliente debe ser persona natural")
                # raise forms.ValidationError('El Cliente debe ser persona natural')

    def __init__(self, *args, **kwargs):
        # Extraer cliente del kwargs o inicial
        cliente_inicial = kwargs.pop("cliente", None)

        super(FacturaBoletaForm, self).__init__(*args, **kwargs)
        self.fields["tipoDocumento"].queryset = TipoDocumento.objects.filter(
            activo=True
        )
        # Si se proporciona un cliente, configurar el queryset para solo ese cliente
        if cliente_inicial:
            self.fields["cliente"].queryset = Persona.objects.filter(
                pk=cliente_inicial.id
            )
            self.initial["cliente"] = (
                cliente_inicial  # Establecer cliente inicial en el formulario
            )
