
from django import forms
from django.forms import inlineformset_factory
from .models import SalidaEncabezado, SalidaDetalle
from dependencias.models import DependenciasBD
from productos.models import Producto  

class SalidaEncabezadoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'num_requi' in self.fields:
            self.fields['num_requi'].widget.attrs['readonly'] = True
            self.fields['num_requi'].widget.attrs['class'] = 'form-control bg-light'

        if 'estado' in self.fields:
            self.fields['estado'].widget.attrs.update({
                'readonly': 'readonly',
                'style': 'color: #3b18d6; font-size: 0.8em; font-weight: bold; border: none; background: transparent;',
                'class': 'form-control'
            })

    fecha_requi = forms.DateField(
        label="Fecha Requis.",
        widget=forms.DateInput(
            format='%Y-%m-%d', # Formato interno para que el HTML5 <input type="date"> lo entienda
            attrs={'class': 'form-control', 'type': 'date'}
        )
    )
    fecha_aprobacion = forms.DateField(
        label="Fecha Aprobacion",
        required=False,
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={'class': 'form-control', 'type': 'date'}
        )
    )

    cod_dependencia_soli = forms.ModelChoiceField(
        queryset=DependenciasBD.objects.all(),
        label="Seleccione Dependencia",
        empty_label="-- Seleccione Dependencia --",
        widget=forms.Select(attrs={'class': 'form-select select2'})
    )

    class Meta:
        model = SalidaEncabezado
        fields = '__all__'

class DetalleSalidaForm(forms.ModelForm):
    # Optimizamos el campo de producto para que no cargue todo si no es necesario
    cod_producto = forms.ModelChoiceField(
        queryset=Producto.objects.all(),
        label="Producto",
        widget=forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%;'})
    )

    class Meta:
        model = SalidaDetalle
        fields = ['cod_producto', 'cant_solicitada', 'cant_entregada']
        widgets = {
            'cant_solicitada': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cant_entregada': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

# --- CLASE BASE PARA OPTIMIZAR EL FORMSET ---
class BaseSalidaDetalleFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        productos = Producto.objects.all()
        for form in self.forms:
            form.fields['cod_producto'].queryset = productos
            # Esto hace que el select diga: "Insumo X (Existencia: 50.00)"
            form.fields['cod_producto'].label_from_instance = lambda obj: f"{obj.descripcion} (COD: {obj.cod_producto}) ({obj.cod_unidad})"


# --- DEFINICIÓN DEL FORMSET OPTIMIZADO ---
SalidaDetalleFormSet = inlineformset_factory(
    SalidaEncabezado, 
    SalidaDetalle,
    form=DetalleSalidaForm,
    formset=BaseSalidaDetalleFormSet, # Se agrega la clase base optimizada
    extra=20, # 🟢 CAMBIO: Bajamos de 50 a 2 para mejorar la velocidad de carga
    can_delete=True
)

# --- CLASE BASE PARA OPTIMIZAR EL FORMSET ---
class BaseSalidaDetalleFormSet2(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        productos = Producto.objects.all()
        for form in self.forms:
            form.fields['cod_producto'].queryset = productos
            # Esto hace que el select diga: "Insumo X (Existencia: 50.00)"
            form.fields['cod_producto'].label_from_instance = lambda obj: f"{obj.descripcion} (COD: {obj.cod_producto}) (Existencia: {obj.cantidad})"

    def clean(self):
        # Validación de seguridad en el servidor
        super().clean()
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE'):
                continue
            
            producto = form.cleaned_data.get('cod_producto')
            entregado = form.cleaned_data.get('cant_entregada') or 0
            
            if producto and entregado > producto.cantidad:
                form.add_error('cant_entregada', f"No puede entregar {entregado}, solo hay {producto.cantidad} en inventario.")

# --- DEFINICIÓN DEL FORMSET OPTIMIZADO ---
SalidaDetalleFormSet2 = inlineformset_factory(
    SalidaEncabezado, 
    SalidaDetalle,
    form=DetalleSalidaForm,
    formset=BaseSalidaDetalleFormSet2, # Se agrega la clase base optimizada
    extra=20, # 🟢 CAMBIO: Bajamos de 50 a 2 para mejorar la velocidad de carga
    can_delete=True
)

class SalidaFilterForm(forms.Form):
    # (Tu código de SalidaFilterForm se mantiene igual...)
    search_query = forms.CharField(required=False, label="Buscar", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Requis., Dependencia...'}))
    num_requi = forms.CharField(required=False, label="N° Requis.", widget=forms.TextInput(attrs={'class': 'form-control'}))
    estado = forms.ChoiceField(choices=[('', '-- Todos --')] + SalidaEncabezado.ESTADO_CHOICES, 
        required=False, label="Status", widget=forms.Select(attrs={'class': 'form-control'}))
    fecha_requi = forms.DateField(required=False, label="Fecha Requis.", widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    fecha_aprobacion = forms.DateField(required=False, label="Fecha Aprobacion", widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    cod_dependencia_soli = forms.ModelChoiceField(queryset=DependenciasBD.objects.all(), required=False, label="Dependencia Solicitante", empty_label="-- Todas --", widget=forms.Select(attrs={'class': 'form-control'}))
