from django import forms
from django.contrib.auth.models import User
from .models import Kategorija, Transakcija, CiljStednje, Racun, Budzet, PonavljajucaTransakcija

class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (css + " form-control").strip()
        # checkbox/select ispravke
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs["class"] = "form-select"

class RegisterForm(BootstrapFormMixin, forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ["username", "email", "password"]

class KategorijaForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Kategorija
        fields = ["naziv", "tip"]

class TransakcijaForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Transakcija
        fields = ["kategorija", "racun", "iznos", "datum", "opis", "doprinos_cilju"]
        widgets = {
            "datum": forms.DateInput(attrs={"type": "date"})
        }

class CiljForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = CiljStednje
        fields = ["naziv", "cilj_iznos", "datum_pocetka", "datum_kraja"]
        widgets = {
            "datum_pocetka": forms.DateInput(attrs={"type": "date"}),
            "datum_kraja": forms.DateInput(attrs={"type": "date"}),
        }

class RacunForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Racun
        fields = ["naziv", "tip", "pocetno_stanje"]
        widgets = {
            "pocetno_stanje": forms.NumberInput(attrs={"step": "0.01"})
        }

class BudzetForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Budzet
        fields = ["kategorija", "iznos", "period", "godina", "mjesec"]
        widgets = {
            "iznos": forms.NumberInput(attrs={"step": "0.01"}),
            "godina": forms.NumberInput(attrs={"min": "2020", "max": "2030"}),
            "mjesec": forms.NumberInput(attrs={"min": "1", "max": "12"})
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['kategorija'].queryset = Kategorija.objects.filter(korisnik=user)

class PonavljajucaTransakcijaForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = PonavljajucaTransakcija
        fields = ["kategorija", "iznos", "opis", "frekvencija", "datum_pocetka", "datum_kraja", "doprinos_cilju"]
        widgets = {
            "iznos": forms.NumberInput(attrs={"step": "0.01"}),
            "datum_pocetka": forms.DateInput(attrs={"type": "date"}),
            "datum_kraja": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['kategorija'].queryset = Kategorija.objects.filter(korisnik=user)
            self.fields['doprinos_cilju'].queryset = CiljStednje.objects.filter(korisnik=user)
