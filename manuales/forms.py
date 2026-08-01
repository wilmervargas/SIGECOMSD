
from django import forms 
from django.forms import inlineformset_factory
from dependencias.models import DependenciasBD
from .models import ManualesDB, ManualesHistoricoDB

# =================================================================
# FORMULARIO PRINCIPAL: Crear/Editar el Manual Actual (Encabezado)
# =================================================================
class ManualForm(forms.ModelForm):
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
        model = ManualesDB
        fields = [
            'id', 'cod_dependencia', 'vigente', 'cod_manual', 'titulo', 
            'fecha_elaboracion', 'fecha_revision', 'fecha_aprobacion', 
            'version', 'distribucion_digital', 'distribucion_fisica', 'observaciones',
            'archivo_pdf'
        ]
        widgets = {
            'id': forms.NumberInput(attrs={'class': 'form-control', 'style': 'color: black;', 'placeholder': 'Ej: 1050'}),
            'cod_dependencia': forms.Select(attrs={'class': 'form-control', 'style': 'color: black;'}),
            'vigente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cod_manual': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black;', 'placeholder': 'Código'}),
            'titulo': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'style': 'color: black; height: 80px;', 'placeholder': 'Título del Manual'}),
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

    def clean_cod_manual(self):
        cod = self.cleaned_data.get('cod_manual')
        return cod.upper() if cod else cod


# =================================================================
# FORMULARIO SECUNDARIO: Detalle Histórico (Bitácora de Versiones)
# =================================================================
class ManualesHistoricoForm(forms.ModelForm):
    class Meta:
        model = ManualesHistoricoDB
        exclude = ['manual']
        widgets = {
            'cod_manual': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black;'}),
            'titulo': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'style': 'color: black; height: 60px;', 'placeholder': 'Título del Manual en esta versión histórica'}),
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


class ManualFilterForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        label='Buscar Código/Descripción Manual', 
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black;', 'placeholder': 'Buscar...'})
    )

# Formset de visualización/edición de históricos vinculados
ManualesHistoricoFormSet = inlineformset_factory(
    ManualesDB,
    ManualesHistoricoDB,
    form=ManualesHistoricoForm,
    extra=1,  # Se cambia a 0 para que no agregue filas vacías de históricos manualmente desde el formset, ya que se controlará automáticamente
    can_delete=True
)