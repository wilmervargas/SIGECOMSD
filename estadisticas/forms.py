
from django import forms
from django.forms import inlineformset_factory
from salidas.models import SalidaEncabezado, SalidaDetalle
from productos.models import Producto  

class EstadisticaEncabezadoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'num_requi' in self.fields:
            self.fields['num_requi'].widget.attrs['readonly'] = True
            self.fields['num_requi'].widget.attrs['class'] = 'form-control bg-light'

        # Status: Azul y pequeño (Lógica de servidor)
        if 'estado' in self.fields:
            self.fields['estado'].widget.attrs.update({
                'readonly': 'readonly',
                'style': 'color: #3b18d6; font-size: 0.8em; font-weight: bold; border: none; background: transparent;',
                'class': 'form-control'
            })


    class Meta:
        model = SalidaEncabezado
        fields = ['num_requi', 'fecha_requi', 'cod_dependencia_soli', 'fecha_aprobacion', 'estado']
        widgets = {
            'fecha_requi': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'fecha_aprobacion': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'cod_dependencia_soli': forms.Select(attrs={'class': 'form-control select2'}),
        }

class DetalleEstadisticaForm(forms.ModelForm):

    cod_producto = forms.ModelChoiceField(
        queryset=Producto.objects.all(),
        empty_label="Seleccione Producto",
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )

    class Meta:
        model = SalidaDetalle
        fields = ['cod_producto', 'cant_solicitada', 'cant_entregada']

# FormSet vinculado correctamente a la clase de arriba
EstadisticaDetalleFormSet = inlineformset_factory(
    SalidaEncabezado, 
    SalidaDetalle,
    form=DetalleEstadisticaForm,
    extra=50, # Aparecerán 3 líneas por defecto
    can_delete=True
)

class EstadisticaFilterForm(forms.Form):
    fecha_requi_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(
            format='%Y-%m-%d', # <--- Formato interno ISO
            attrs={
                'type': 'date', # <--- ESTO activa el calendario y la visualización
                'class': 'form-control'
            }
        )
    )
    
    fecha_requi_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date', 
                'class': 'form-control'
            }
        )
    )
    # Cambia el CharField por ChoiceField
    estado = forms.ChoiceField(
        choices=[('', '-- Todos --')] + SalidaEncabezado.ESTADO_CHOICES,
        required=False,
        label="Status",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
