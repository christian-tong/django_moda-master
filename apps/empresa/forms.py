from django import forms
from .models import Conductor, Agencia


class ConductorForm(forms.ModelForm):
    class Meta:
        model = Conductor
        fields = "__all__"

        widgets = {
            "fechaExpedicion": forms.DateInput(attrs={"type": "date"}),
            "fechaRevalidacion": forms.DateInput(attrs={"type": "date"}),
        }


class AgenciaForm(forms.ModelForm):
    class Meta:
        model = Agencia
        exclude = ["empresa", "tipo"]
