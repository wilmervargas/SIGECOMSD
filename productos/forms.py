
from django import forms 
from django.forms import inlineformset_factory # NUEVA IMPORTACIÓN
from categorias.models import CategoriaBD
from unidades.models import UnidadBD
from .models import Producto

# Asegúrate de importar Unidad también si la usas en el form
# Nota: La referencia a ArticuloBase se elimina ya que Producto ahora es el SKU.

# =================================================================
# Formulario para Crear/Editar un Producto (SKU/Variación)
# =================================================================

class ProductosForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['imagen'].required = False
        # Accede a la instancia del modelo si existe
        instance = getattr(self, 'instance', None)
        if instance and instance.cod_producto:
            # Si codigo tiene valor, hacer el campo readonly
            self.fields['cod_producto'].widget.attrs['readonly'] = 'readonly'
            self.fields['descripcion'].widget.attrs['autofocus'] = 'True'
        else:
            self.fields['cod_producto'].widget.attrs['autofocus'] = 'True'

    # Definimos el campo 'activo' explícitamente como ChoiceField
    # Cambiamos a TypedChoiceField para asegurar que devuelve valores booleanos reales
    activo = forms.TypedChoiceField(
        choices=[(True, 'Sí (Activo)'), (False, 'No (Inactivo)')],
        coerce=lambda x: x == 'True',
        initial=True,
        label='Insumo Activo?',
        widget=forms.Select(attrs={'style': 'color: black;'})
    )

    observaciones = forms.CharField(
        required=False,
        label='Observaciones del Insumo',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,  # Esto le da altura para que sea cómodo editar
            'placeholder': 'Escriba notas adicionales aquí...',
            'style': 'color: black; resize: none;'
        })
    )

    class Meta:
        model = Producto
        fields = [
            'cod_producto', 'descripcion', 'cod_unidad', 'cod_categoria', 
            'stock_minimo_global', 'stock_maximo', 'cantidad',
            'costo_compra', 'activo', 
            'imagen', 'observaciones' # 💡 Asegúrate que esté en la lista
        ]

        widgets = {
            'cod_producto': forms.TextInput(attrs={'style': 'color: black;', 'autofocus': 'autofocus'}),
            'descripcion': forms.Textarea(attrs={'rows': 3, 'style': 'color: black;'}),
            'cod_unidad': forms.Select(attrs={'style': 'color: black;'}),
            'cod_categoria': forms.Select(attrs={'style': 'color: black;'}),
        }

    def clean_cod_producto(self):
        """Convierte el campo 'cod_producto' (SKU) a mayúsculas antes de guardar."""
        sku = self.cleaned_data.get('cod_producto')
        if sku:
            return sku.upper()
        return sku
    

# =================================================================
# Formulario para Filtrar el Listado de Inventario (Adaptado)
# =================================================================

class ProductosFilterForm(forms.Form):
    search_query = forms.CharField(
        required=False,
        label='Buscar Codigo/Descrip. de Insumo', 
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': 'color: black;', 'placeholder': 'escribe codigo/descripción'})
    )
    
    # Campo 'articulo_base' se mantiene por compatibilidad, pero apunta al modelo Producto
    categoria = forms.ModelChoiceField(
        queryset=CategoriaBD.objects.all(),
        required=False,
        label='Filtrar por Categoría',
        empty_label="-- Todos --",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    unidad = forms.ModelChoiceField(
        queryset=UnidadBD.objects.all(),
        required=False,
        label='Filtrar por Unidad',
        empty_label="-- Todos --",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    alerta_stock = forms.ChoiceField(
        choices=[('', '-- Todos --'), ('MIN', '⚠️ Stock Bajo'), ('MAX', '✅ Stock normal')],
        required=False,
        label='Filtro por Stock',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Opción 1: ChoiceField (más sencillo)
    lactivo = forms.ChoiceField(
        required=False,
        label='STATUS',
        initial = 'True', # <--- Mantiene 'Activos' seleccionado por defecto
        choices=(
            ('True', '✅ Activos'), # <--- Sale de primero en la lista
            ('False', '❌ Inactivos'),
            ('Or', '-- Todos --'),
        ),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
