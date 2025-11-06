from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Aeroporto, Reserva, Assento, Cliente

class SignUpForm(forms.Form):
    nome = forms.CharField(max_length=120, label="Nome completo")
    email = forms.EmailField(label="Email")
    cpf = forms.CharField(max_length=11, label="CPF", required=False)  # <- opcional
    data_nascimento = forms.DateField(label="Data de nascimento", required=False,
                                      widget=forms.DateInput(attrs={"type":"date"}))
    password1 = forms.CharField(label="Senha", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirme a senha", widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Já existe um usuário com este e-mail.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "As senhas não coincidem.")
        if p1:
            validate_password(p1)  # <- pode reprovar senha fraca
        return cleaned

    def save(self):
        email = self.cleaned_data["email"].lower()
        user = User.objects.create_user(
            username=email,
            email=email,
            password=self.cleaned_data["password1"],
            first_name=self.cleaned_data["nome"],
        )
        # cria/garante Cliente por e-mail (sem mexer nos modelos)
        Cliente.objects.get_or_create(
            email=email,
            defaults={
                "nome": self.cleaned_data["nome"],
                "cpf": self.cleaned_data.get("cpf") or "",
                "data_nascimento": self.cleaned_data.get("data_nascimento"),
            },
        )
        return user


class SearchVoosForm(forms.Form):
    origem = forms.ModelChoiceField(queryset=Aeroporto.objects.all(), label="Origem")
    destino = forms.ModelChoiceField(queryset=Aeroporto.objects.all(), label="Destino")
    data = forms.DateField(label="Data", widget=forms.DateInput(attrs={"type":"date"}))

    def clean(self):
        cleaned = super().clean()
        o = cleaned.get("origem")
        d = cleaned.get("destino")
        if o and d and o == d:
            self.add_error("destino", "Origem e destino não podem ser iguais.")
        return cleaned

class ReservaAssentoForm(forms.Form):
    assento_id = forms.IntegerField(widget=forms.HiddenInput)