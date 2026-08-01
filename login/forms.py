'''
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    # Puedes repetir esto para cualquier otro campo de texto que desees en mayúsculas
    def clean_username(self):
        usuario = self.cleaned_data.get('username')
        if usuario:
            return usuario.lower()
        return usuario

    def clean_last_name(self):
        """Convierte el campo 'nombres' a mayúsculas antes de guardar."""
        apellidos = self.cleaned_data.get('last_name')
        # Verifica que no sea None o vacío antes de aplicar .upper()
        if apellidos:
            return apellidos.upper()
        return apellidos
    
    def clean_first_name(self):
        """Convierte el campo 'apellidos' a mayúsculas antes de guardar."""
        nombres = self.cleaned_data.get('first_name')
        if nombres:
            return nombres.upper()
        return nombres
    
    # Puedes repetir esto para cualquier otro campo de texto que desees en mayúsculas
    def clean_email(self):
        correo = self.cleaned_data.get('email')
        if correo:
            return correo.lower()
        return correo
    
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ("username", 'first_name', 'last_name', 'email', 'password1', 'password2')
    
        def save(self, commit=True):
            user = super(CustomUserCreationForm, self).save(commit=False)
            user.email = self.cleaned_data['email']
            
            if commit:
                user.save
            return user


class CustomUserChangeForm(UserChangeForm):

    # Puedes repetir esto para cualquier otro campo de texto que desees en mayúsculas
    def clean_username(self):
        usuario = self.cleaned_data.get('username')
        if usuario:
            return usuario.lower()
        return usuario

    def clean_last_name(self):
        """Convierte el campo 'nombres' a mayúsculas antes de guardar."""
        apellidos = self.cleaned_data.get('last_name')
        # Verifica que no sea None o vacío antes de aplicar .upper()
        if apellidos:
            return apellidos.upper()
        return apellidos
    
    def clean_first_name(self):
        """Convierte el campo 'apellidos' a mayúsculas antes de guardar."""
        nombres = self.cleaned_data.get('first_name')
        if nombres:
            return nombres.upper()
        return nombres
    
    # Puedes repetir esto para cualquier otro campo de texto que desees en mayúsculas
    def clean_email(self):
        correo = self.cleaned_data.get('email')
        if correo:
            return correo.lower()
        return correo

    class Meta:
        model = User
        fields = ("username", 'first_name', 'last_name', 'email')
        
        def save(self, commit=True):
            #user = super(CustomUserCreationForm, self).save(commit=False)
            user = super(CustomUserChangeForm, self).save(commit=False)
            user.email = self.cleaned_data['email']
            
            if commit:
                user.save
            return user
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.fields['imagen'].required = False
        # Accede a la instancia del modelo si existe
        instance = getattr(self, 'instance', None)
        if instance and instance.username:
            # Si usuario tiene valor, hacer el campo readonly
            self.fields['username'].widget.attrs['readonly'] = 'readonly'
            self.fields['first_name'].widget.attrs['autofocus'] = 'True'
        else:
            self.fields['username'].widget.attrs['autofocus'] = 'True'
'''
