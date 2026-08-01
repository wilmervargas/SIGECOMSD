from django import forms 
from .models import DependenciasBD

# =========================='=======================================
# NUEVO: Formulario para Crear/Editar una Dependencias
# =================================================================

class DependenciasFilterForm(forms.Form):
    # Este campo se usa para buscar tanto en cedula como en nombres y apellidos
    search_query = forms.CharField(
        label='Buscar por Código', 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 
                'style': 'color: black;', 
                'placeholder': 'escribe Código'}))

class DependenciasForm(forms.ModelForm):

    def clean_cod_dependencia(self):
        """Convierte el campo 'nombres y apellidos' a mayúsculas antes de guardar."""
        cod_dependencia = self.cleaned_data.get('cod_dependencia')
        # Verifica que no sea None o vacío antes de aplicar .upper()
        if cod_dependencia:
            return cod_dependencia.upper()
        return cod_dependencia

    def clean_descripcion(self):
        """Convierte el campo 'descripcion' a mayúsculas antes de guardar."""
        descripcion = self.cleaned_data.get('descripcion')
        # Verifica que no sea None o vacío antes de aplicar .upper()
        if descripcion:
            return descripcion.upper()
        return descripcion

    def clean_observaciones(self):
        """Convierte el campo 'observaciones' a mayúsculas antes de guardar."""
        observaciones = self.cleaned_data.get('observaciones')
        # Verifica que no sea None o vacío antes de aplicar .upper()
        if observaciones:
            return observaciones.upper()
        return observaciones

    class Meta:
        model = DependenciasBD
        #fields = '__all__'

        fields = ['id', 'cod_dependencia', 'descripcion', 'observaciones']
        labels = {
            'id':'ID:',
            'cod_dependencia':'Cod. Dependencia:',
            'descripcion':'Descripción:',
            'observaciones':'Observaciones:',
        }
    
        #readonly_attr = {'readonly': 'readonly'} if not model.cedula else {}
        widgets = {
            'id': forms.TextInput(attrs={'placeholder': 'ID'}),
            'cod_dependencia': forms.TextInput(attrs={'placeholder': 'Escribe Codigo', 'style': 'width: 250px;'}),
            'descripcion': forms.Textarea(attrs={'placeholder': 'Descripcion', 'rows': 3, 'style': 'width: 400px;'}),
            'observaciones': forms.Textarea(attrs={'placeholder': 'Escribe la observación', 'rows': 3, 'style': 'width: 400px;'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['imagen'].required = False
        # Accede a la instancia del modelo si existe
        instance = getattr(self, 'instance', None)
        if instance and instance.cod_dependencia:
            # Si codigo tiene valor, hacer el campo readonly
            self.fields['cod_dependencia'].widget.attrs['readonly'] = 'readonly'
            self.fields['descripcion'].widget.attrs['autofocus'] = 'True'
        else:
            self.fields['cod_dependencia'].widget.attrs['autofocus'] = 'True'
