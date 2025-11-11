from django import forms
from django.contrib.auth.models import User
from .models import Recurso, UserProfile

class RecursoForm(forms.ModelForm):
    class Meta:
        model = Recurso
        fields = ['titulo', 'descripcion', 'tipo_recurso', 'categoria', 'contenido', 'es_publico']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del recurso'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del recurso'}),
            'tipo_recurso': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Contenido del recurso...'}),
            'es_publico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['tipo_usuario']
        widgets = {
            'tipo_usuario': forms.Select(attrs={'class': 'form-control'}),
        }