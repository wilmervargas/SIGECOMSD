from django import forms 
from .models import CategoriaBD

# =================================================================
# NUEVO: Formulario para Crear/Editar una Categoría
# =================================================================

class CategoriaFilterForm(forms.Form):
    # Este campo se usa para buscar tanto en cod_categoria como en descripcion
    search_query = forms.CharField(
        label='Buscar por Código o Descripción', 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 
                'style': 'color: black;', 
                'placeholder': 'escribe código/descripción'}))

class CategoriaForm(forms.ModelForm):


    def clean_cod_categoria(self):
        """Convierte el campo 'descipcion' a mayúsculas antes de guardar."""
        cod_categoria = self.cleaned_data.get('cod_categoria')
        # Verifica que no sea None o vacío antes de aplicar .upper()
        if cod_categoria:
            return cod_categoria.upper()
        return cod_categoria

    def clean_descripcion(self):
        """Convierte el campo 'descipcion' a mayúsculas antes de guardar."""
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
        model = CategoriaBD
        #fields = '__all__'

        fields = ['id', 'cod_categoria', 'descripcion', 'observaciones']
        labels = {
            'id':'ID:',
            'cod_categoria':'Cod. Categoría:',
            'descripcion':'Descripción:',
            'observaciones':'Observaciones:',
        }
    
        #readonly_attr = {'readonly': 'readonly'} if not model.cedula else {}

        widgets = {
            'id': forms.TextInput(attrs={'placeholder': 'ID'}),
            'cod_categoria': forms.TextInput(attrs={'placeholder': 'Escribe Cod Categoría', 'style': 'width: 250px;'}),
            'descripcion': forms.Textarea(attrs={'placeholder': 'Escribe la descripción', 'rows': 3, 'style': 'width: 400px;'}),
            'observaciones': forms.Textarea(attrs={'placeholder': 'Escribe la observación', 'rows': 3, 'style': 'width: 400px;'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['imagen'].required = False
        # Accede a la instancia del modelo si existe
        instance = getattr(self, 'instance', None)
        if instance and instance.cod_categoria:
            # Si codigo tiene valor, hacer el campo readonly
            self.fields['cod_categoria'].widget.attrs['readonly'] = 'readonly'
            self.fields['descripcion'].widget.attrs['autofocus'] = 'True'
        else:
            self.fields['cod_categoria'].widget.attrs['autofocus'] = 'True'
