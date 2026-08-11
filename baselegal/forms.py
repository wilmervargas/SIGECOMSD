
from django import forms 
from django.forms import inlineformset_factory
from .models import BaselegalDB, BaselegalHistoricoDB

# =================================================================
# FORMULARIO PRINCIPAL: Crear/Editar el Baselegal Actual (Encabezado)
# =================================================================
class BaselegalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        
        if instance and instance.pk:
            if 'id' in self.fields:
                self.fields['id'].widget.attrs['readonly'] = 'readonly'
            if 'titulo' in self.fields:
                self.fields['titulo'].widget.attrs['autofocus'] = 'True'
        else:
            if 'id' in self.fields:
                self.fields['id'].widget.attrs['autofocus'] = 'True'

    class Meta:
        model = BaselegalDB
        fields = [
            'id', 'vigente', 'cod_baselegal', 'titulo', 
            'fecha_aprobacion', 'fecha_publicacion', 'nro_gaceta', 'tipo', 'organo_publica',
            'distribucion_digital', 'distribucion_fisica', 'observaciones',
            'archivo_pdf'
        ]
        widgets = {
            'id': forms.NumberInput(attrs={'class': 'form-control', 'style': 'color: black;', 'placeholder': 'Ej: 1050'}),
            'vigente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cod_baselegal': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black;', 'placeholder': 'Código'}),
            'titulo': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'style': 'color: black; height: 80px;', 'placeholder': 'Título de Base Legal'}),
            'fecha_aprobacion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'fecha_publicacion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'nro_gaceta': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black;', 'placeholder': 'Número de Gaceta'}),
            'tipo': forms.Select(attrs={'class': 'form-control', 'style': 'color: black;'}),
            'organo_publica': forms.Select(attrs={'class': 'form-control', 'style': 'color: black;'}),
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

    def clean_cod_baselegal(self):
        cod = self.cleaned_data.get('cod_baselegal')
        return cod.upper() if cod else cod


# =================================================================
# FORMULARIO SECUNDARIO: Detalle Histórico (Bitácora de Versiones)
# =================================================================
class BaselegalHistoricoForm(forms.ModelForm):
    class Meta:
        model = BaselegalHistoricoDB
        exclude = ['baselegal']
        widgets = {
            'cod_baselegal': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black;', 'placeholder': 'Código'}),
            'titulo': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'style': 'color: black; height: 80px;', 'placeholder': 'Título de Base Legal'}),
            'fecha_aprobacion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'fecha_publicacion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'nro_gaceta': forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black;', 'placeholder': 'Número de Gaceta'}),
            'tipo': forms.Select(attrs={'class': 'form-control', 'style': 'color: black;'}),
            'organo_publica': forms.Select(attrs={'class': 'form-control', 'style': 'color: black;'}),
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


class BaselegalFilterForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        label='Buscar Código/Descripción Base legal', 
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black;', 'placeholder': 'Buscar...'})
    )

# Formset de visualización/edición de históricos vinculados
BaselegalHistoricoFormSet = inlineformset_factory(
    BaselegalDB,
    BaselegalHistoricoDB,
    form=BaselegalHistoricoForm,
    extra=1,  # Se cambia a 0 para que no agregue filas vacías de históricos manualmente desde el formset, ya que se controlará automáticamente
    can_delete=True
)