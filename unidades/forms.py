from django import forms 
from .models import UnidadBD

# =================================================================
# NUEVO: Formulario para Crear/Editar una unidad
# =================================================================

class UnidadFilterForm(forms.Form):
    # Este campo se usa para buscar tanto en cod_unidad como en descripcion
    search_query = forms.CharField(
        label='Buscar por Código o Descripción', 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 
                'style': 'color: black;', 
                'placeholder': 'escribe código/descripción'}))

class UnidadForm(forms.ModelForm):

    def clean_cod_unidad(self):
        """Convierte el `ca`mpo 'descipcion' a mayúsculas antes de guardar."""
        cod_unidad = self.cleaned_data.get('cod_unidad')
        # Verifica que no sea None o vacío antes de aplicar .upper()
        if cod_unidad:
            return cod_unidad.upper()
        return cod_unidad

    def clean_descripcion(self):
        """Convierte el `ca`mpo 'descipcion' a mayúsculas antes de guardar."""
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
        model = UnidadBD
        #fields = '__all__'

        fields = ['id', 'cod_unidad', 'descripcion', 'observaciones']
        labels = {
            'id':'ID:',
            'cod_unidad':'Cod. Unidad:',
            'descripcion':'Descripción:',
            'observaciones':'Observaciones:',
        }
    
        #readonly_attr = {'readonly': 'readonly'} if not model.cedula else {}

        widgets = {
            'id': forms.TextInput(attrs={'placeholder': 'ID'}),
            'cod_unidad': forms.TextInput(attrs={'placeholder': 'Escribe Cod Unidad', 'style': 'width: 250px;'}),
            'descripcion': forms.Textarea(attrs={'placeholder': 'Escribe la descripción', 'rows': 3, 'style': 'width: 400px;'}),
            'observaciones': forms.Textarea(attrs={'placeholder': 'Escribe la observación', 'rows': 3, 'style': 'width: 400px;'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['imagen'].required = False
        # Accede a la instancia del modelo si existe
        instance = getattr(self, 'instance', None)
        if instance and instance.cod_unidad:
            # Si codigo tiene valor, hacer el campo readonly
            self.fields['cod_unidad'].widget.attrs['readonly'] = 'readonly'
            self.fields['descripcion'].widget.attrs['autofocus'] = 'True'
        else:
            self.fields['cod_unidad'].widget.attrs['autofocus'] = 'True'
