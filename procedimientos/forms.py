from django import forms 
from django.forms import inlineformset_factory
from dependencias.models import DependenciasBD
from .models import ProcedimientosDB, ProcedimientosHistoricoDB

# =================================================================
# FORMULARIO PRINCIPAL: Crear/Editar el Procedimiento Actual (Encabezado)
# =================================================================
class ProcedimientoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        
        if instance and instance.pk:
            if 'id' in self.fields:
                self.fields['id'].widget.attrs['readonly'] = 'readonly'
            if 'cod_dependencia' in self.fields:
                self.fields['cod_dependencia'].widget.attrs['autofocus'] = 'True'
        else:
            if 'id' in self.fields:
                self.fields['id'].widget.attrs['autofocus'] = 'True'

    class Meta:
        model = ProcedimientosDB
        fields = [
            'id', 'cod_dependencia', 'vigente', 'cod_procedimiento', 'titulo', 
            'fecha_elaboracion', 'fecha_revision', 'fecha_aprobacion', 
            'version', 'distribucion_digital', 'distribucion_fisica', 'observaciones',
            'archivo_pdf'
        ]
        widgets = {
            'id': forms.NumberInput(attrs={'class': 'form-control', 'style': 'color: black;', 'placeholder': 'Ej: 1050'}),
            'cod_dependencia': forms.Select(attrs={'class': 'form-control', 'style': 'color: black;'}),
            'vigente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cod_procedimiento': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black;', 'placeholder': 'Código'}),
            'titulo': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'style': 'color: black; height: 80px;', 'placeholder': 'Título del Procedimiento'}),
            'fecha_elaboracion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'fecha_revision': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'fecha_aprobacion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'version': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black;', 'placeholder': 'Ej: 1.0'}),
            # CAMBIO AQUÍ: Convertidos a listas desplegables (Select) de Sí/No
            'distribucion_digital': forms.Select(
                choices=[(True, 'Sí'), (False, 'No')],
                attrs={'class': 'form-control', 'style': 'color: black;'}
            ),
            'distribucion_fisica': forms.Select(
                choices=[(True, 'Sí'), (False, 'No')],
                attrs={'class': 'form-control', 'style': 'color: black;'}
            ),
            'observaciones': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'style': 'color: black; height: 80px;', 'placeholder': 'Observaciones actuales'}),
            'archivo_pdf': forms.ClearableFileInput(attrs={'class': 'form-control', 'style': 'color: black; background: white;'}),
        }

    def clean_cod_procedimiento(self):
        cod = self.cleaned_data.get('cod_procedimiento')
        return cod.upper() if cod else cod


# =================================================================
# FORMULARIO SECUNDARIO: Detalle Histórico (Bitácora de Versiones)
# =================================================================
class ProcedimientosHistoricoForm(forms.ModelForm):
    class Meta:
        model = ProcedimientosHistoricoDB
        exclude = ['procedimiento']
        widgets = {
            'cod_procedimiento': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black;'}),
            'titulo': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'style': 'color: black; height: 60px;', 'placeholder': 'Título del Procedimiento en esta versión histórica'}),
            'fecha_elaboracion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'fecha_revision': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'fecha_aprobacion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'version': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black;'}),
            # CAMBIO AQUÍ: Convertidos a listas desplegables (Select) de Sí/No
            'distribucion_digital': forms.Select(
                choices=[(True, 'Sí'), (False, 'No')],
                attrs={'class': 'form-control', 'style': 'color: black;'}
            ),
            'distribucion_fisica': forms.Select(
                choices=[(True, 'Sí'), (False, 'No')],
                attrs={'class': 'form-control', 'style': 'color: black;'}
            ),
            'observaciones': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'style': 'color: black; height: 60px;', 'placeholder': 'Observaciones para esta versión histórica'}),
            'archivo_pdf': forms.ClearableFileInput(attrs={'class': 'form-control', 'style': 'color: black; background: white;'}),
        }


class ProcedimientoFilterForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        label='Buscar Código/Descripción Procedimiento', 
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black;', 'placeholder': 'Buscar...'})
    )

# Formset de visualización/edición de históricos vinculados
ProcedimientosHistoricoFormSet = inlineformset_factory(
    ProcedimientosDB,
    ProcedimientosHistoricoDB,
    form=ProcedimientosHistoricoForm,
    extra=1,  # Se cambia a 0 para que no agregue filas vacías de históricos manualmente desde el formset, ya que se controlará automáticamente
    can_delete=True
)