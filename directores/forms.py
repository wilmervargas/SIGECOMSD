from django import forms 
from django.forms import inlineformset_factory
from .models import DirectoresBD, DependeciasDirectorBD
from dependencias.models import DependenciasBD

# =================================================================
# Formulario de Filtro para el Listado
# =================================================================
class DirectoresFilterForm(forms.Form):
    search_query = forms.CharField(
        label='Buscar por Codigo', 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'style': 'color: black;', 
            'placeholder': 'escribe Codigo'
        })
    )

# =================================================================
# Formulario Principal para Crear/Editar Directores
# =================================================================
class DirectoresForm(forms.ModelForm):
    # --- Métodos de limpieza se mantienen igual ---
    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        return cedula.upper() if cedula else cedula

    def clean_nombres_apellidos(self):
        nombres_apellidos = self.cleaned_data.get('nombres_apellidos')
        return nombres_apellidos.upper() if nombres_apellidos else nombres_apellidos

    def clean_observaciones(self):
        observaciones = self.cleaned_data.get('observaciones')
        return observaciones.upper() if observaciones else observaciones

    class Meta:
        model = DirectoresBD
        # Quitamos cod_dependencia de aquí
        fields = ['id', 'cedula', 'nombres_apellidos', 'usuario', 'observaciones']
        labels = {
            'id': 'ID:',
            'cedula': 'Codigo:',
            'nombres_apellidos': 'Nombres y Apellidos:',
            'usuario': 'Usuario:',
            'observaciones': 'Observaciones:',
        }
    
        widgets = {
            'id': forms.TextInput(attrs={'placeholder': 'ID'}),
            'cedula': forms.TextInput(attrs={'placeholder': 'Escribe Codigo', 'style': 'width: 250px;', 'class': 'form-control'}),
            'nombres_apellidos': forms.Textarea(attrs={'placeholder': 'Nombres y Apellidos', 'rows': 3, 'style': 'width: 400px;', 'class': 'form-control'}),
            'usuario': forms.TextInput(attrs={'placeholder': 'Usuario', 'style': 'width: 200px;', 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'placeholder': 'Escribe la observación', 'rows': 3, 'style': 'width: 400px;', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance and instance.cedula:
            self.fields['cedula'].widget.attrs['readonly'] = 'readonly'

# Definición del Subformulario para Dependencias
DependenciasFormSet = inlineformset_factory(
    DirectoresBD, 
    DependeciasDirectorBD,
    fields=('dependencia', 'cargo', 'activo'),
    extra=3, # Una fila vacía para agregar
    can_delete=True,
    widgets={
        'dependencia': forms.Select(attrs={'class': 'form-control', 'style': 'color: black; width: 350px;'}),
        'cargo': forms.Select(attrs={'class': 'form-control', 'style': 'color: black; width: 150px;'}),
    }
)
