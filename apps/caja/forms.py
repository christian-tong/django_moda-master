from django import forms
from django.forms import BaseFormSet
from .models import Caja, MovimientoCaja, MedioPago
from apps.persona.models import Persona


class CajaForm(forms.ModelForm):
    cajeros = forms.ModelMultipleChoiceField(
        queryset=Persona.objects.filter(ispersonal=True), required=True
    )

    class Meta:
        model = Caja
        exclude = ["montoEntrada", "montoSalida", "saldo"]

        widgets = {
            "agencia": forms.Select(attrs={"class": "select"}),
            "cajeros": forms.Select(attrs={"class": "select"}),
        }


class MovimientoCajaForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=Persona.objects.filter(numDoc="44319644"),
        empty_label="Select an author",
    )

    class Meta:
        model = MovimientoCaja
        fields = "__all__"

        widgets = {"movFecha": forms.DateInput(attrs={"type": "date"})}


class MedioPagoForm(forms.ModelForm):
    class Meta:
        model = MedioPago
        fields = "__all__"

        widgets = {
            "monto": forms.NumberInput(attrs={"onkeyup": "total_pago()"}),
            "tipoMedioPago": forms.Select(attrs={"class": "select"}),
        }


class BaseMedioPagoFormSet(BaseFormSet):
    def clean(self):
        cont = 0
        for form in self.forms:
            monto = form.cleaned_data.get("monto")
            tipomedio_pago = form.cleaned_data.get("tipoMedioPago")

            if monto is None or monto < 1.0:
                self._errors[cont]["monto"] = self.error_class(["es obligado"])

            if tipomedio_pago is None:
                self._errors[cont]["tipoMedioPago"] = self.error_class(["es obligado"])

            cont += 1
        return self
