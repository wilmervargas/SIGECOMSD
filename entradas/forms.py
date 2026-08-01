
from django import forms
from django.forms import inlineformset_factory
from .models import EntradaEncabezado, EntradaDetalle
from proveedores.models import ProveedoresBD  
from productos.models import Producto  

class EntradaEncabezadoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'num_orden' in self.fields:
            self.fields['num_orden'].widget.attrs['readonly'] = True
            self.fields['num_orden'].widget.attrs['class'] = 'form-control bg-light'

        # Status: Azul y pequeño (Lógica de servidor)
        if 'estado' in self.fields:
            self.fields['estado'].widget.attrs.update({
                'readonly': 'readonly',
                'style': 'color: #3b18d6; font-size: 0.8em; font-weight: bold; border: none; background: transparent;',
                'class': 'form-control'
            })

    ced_proveedor = forms.ModelChoiceField(
        queryset=ProveedoresBD.objects.all(),
        label="Seleccione Proveedor",
        empty_label="-- Seleccione un Proveedor --",
        widget=forms.Select(attrs={'class': 'form-select select2'})
    )

    class Meta:
        model = EntradaEncabezado
        fields = ['num_orden', 'fecha_orden', 'num_factura', 'fecha_factura', 'monto_factura', 'ced_proveedor', 'estado']
        widgets = {
            'fecha_orden': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_factura': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'monto_factura': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

# Clase personalizada para mostrar información extra del producto en el Select
class ProductoChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.descripcion} ({obj.cod_producto}) - UND: {obj.cod_unidad} - Stock: {obj.cantidad}"

class DetalleEntradaForm(forms.ModelForm):
    cod_producto = ProductoChoiceField(
        queryset=Producto.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select select2', 'style': 'width: 100%;'})
    )
    
    # Campo informativo de stock actual
    cantidad = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'readonly': 'readonly', 
            'class': 'form-control bg-light text-center',
            'style': 'border: none; font-weight: bold;'
        })
    )

    class Meta:
        model = EntradaDetalle
        fields = ['cod_producto', 'cant_recibida']
        widgets = {
            'cant_recibida': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Llenar el campo 'cantidad' (stock) si ya existe el registro
        if self.instance and self.instance.pk and self.instance.cod_producto:
            self.fields['cantidad'].initial = self.instance.cod_producto.cantidad

# --- CLASE BASE PARA OPTIMIZAR EL RENDIMIENTO ---
class BaseEntradaDetalleFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 🟢 OPTIMIZACIÓN: Una sola consulta de productos para todos los formularios
        # Usamos select_related para traer también la unidad de medida de un solo golpe
        productos = Producto.objects.all().select_related('cod_unidad')
        for form in self.forms:
            form.fields['cod_producto'].queryset = productos


# --- FORMSET OPTIMIZADO ---
EntradaDetalleFormSet = inlineformset_factory(
    EntradaEncabezado, 
    EntradaDetalle,
    form=DetalleEntradaForm,
    formset=BaseEntradaDetalleFormSet, # Agregamos la optimización
    extra=50, # 🟢 REDUCIDO de 50 a 2 para que cargue instantáneo
    can_delete=True
)

class EntradaFilterForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        label="Buscar",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Orden, Factura o Proveedor...'
        })
    )
    num_orden = forms.CharField(
        required=False,
        label="N° Orden",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    estado = forms.ChoiceField(
        choices=[('', '-- Todos --')] + EntradaEncabezado.ESTADO_CHOICES,
        required=False,
        label="Status",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    fec_orden = forms.DateField(
        required=False,
        label="Fecha Orden",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    num_factura = forms.CharField(
        required=False,
        label="N° Factura",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    fec_factura = forms.DateField(
        required=False,
        label="Fecha Factura",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )    
    ced_proveedor = forms.ModelChoiceField(
        queryset=ProveedoresBD.objects.all(),
        required=False,
        label="Proveedor",
        empty_label="-- Todos los Proveedores --",
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )