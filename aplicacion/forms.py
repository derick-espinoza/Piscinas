from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import UsuarioPersonalizado 

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    edad = forms.IntegerField(required=False)
    pais = forms.CharField(max_length=100, required=False)
    numero_telefono = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = UsuarioPersonalizado  
        fields = ['username', 'email', 'password1', 'password2', 'edad', 'pais', 'numero_telefono']
