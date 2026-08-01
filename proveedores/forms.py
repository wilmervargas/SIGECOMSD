from django import forms 
from .models import ProveedoresBD

# =========================='=======================================
# NUEVO: Formulario para Crear/Editar una ProveedoresBD
# =================================================================

class ProveedoresFilterForm(forms.Form):
    # Este campo se usa para buscar tanto en cedula como en nombres y apellidos
    search_query = forms.CharField(
        label='Buscar por Cédula', 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 
                'style': 'color: black;', 
                'placeholder': 'escribe cédula'}))

class ProveedoresForm(forms.ModelForm):

    def clean_ced_proveedor(self):
        """Convierte el campo 'nombres y apellidos' a mayúsculas antes de guardar."""
        ced_proveedor = self.cleaned_data.get('ced_proveedor')
        # Verifica que no sea None o vacío antes de aplicar .upper()
        if ced_proveedor:
            return ced_proveedor.upper()
        return ced_proveedor

    def clean_nombres_apellidos(self):
        """Convierte el campo 'nombres_apellidos' a mayúsculas antes de guardar."""
        nombres_apellidos = self.cleaned_data.get('nombres_apellidos')
        # Verifica que no sea None o vacío antes de aplicar .upper()
        if nombres_apellidos:
            return nombres_apellidos.upper()
        return nombres_apellidos

    def clean_cedula_representante(self):
        """Convierte el campo 'cedula' a mayúsculas antes de guardar."""
        cedula_representante = self.cleaned_data.get('cedula_representante')
        # Verifica que no sea None o vacío antes de aplicar .upper()
        if cedula_representante:
            return cedula_representante.upper()
        return cedula_representante

    def clean_nombres_representante(self):
        """Convierte el campo 'nombres' a mayúsculas antes de guardar."""
        nombres_representante = self.cleaned_data.get('nombres_representante')
        # Verifica que no sea None o vacío antes de aplicar .upper()
        if nombres_representante:
            return nombres_representante.upper()
        return nombres_representante

    def clean_direccion(self):
        """Convierte el campo 'direccion' a mayúsculas antes de guardar."""
        # Extraemos 'direccion', que es el nombre real del campo
        direccion = self.cleaned_data.get('direccion')
        
        if direccion:
            return direccion.upper()
        return direccion

    def clean_telefonos(self):
        """Convierte el campo 'telefonosobservaciones' a mayúsculas antes de guardar."""
        telefonos = self.cleaned_data.get('telefonos')
        # Verifica que no sea None o vacío antes de aplicar .upper()
        if telefonos:
            return telefonos.upper()
        return telefonos

    def clean_observaciones(self):
        """Convierte el campo 'observaciones' a mayúsculas antes de guardar."""
        observaciones = self.cleaned_data.get('observaciones')
        # Verifica que no sea None o vacío antes de aplicar .upper()
        if observaciones:
            return observaciones.upper()
        return observaciones

    class Meta:
        model = ProveedoresBD
        #fields = '__all__'

        fields = ['id', 'ced_proveedor', 'nombres_apellidos','cedula_representante','nombres_representante','direccion','telefonos', 'observaciones']
        labels = {
            'id':'ID:',
            'ced_proveedor':'Ced. Proveedor/RIF:',
            'nombres_apellidos':'Nombres y Apellidos/Razón Social:',
            'cedula_representante':'Cédula Representante:',
            'nombres_representante':'Nombres Representante:',
            'direccion':'Dirección:',
            'telefonos':'Teléfonos:',
            'observaciones':'Observaciones:',
        }
    
        #readonly_attr = {'readonly': 'readonly'} if not model.cedula else {}
        widgets = {
            'id': forms.TextInput(attrs={'placeholder': 'ID'}),
            'ced_proveedor': forms.TextInput(attrs={'placeholder': 'Escribe Cedula Proveedor/RIF', 'style': 'width: 250px;'}),
            'nombres_apellidos': forms.Textarea(attrs={'placeholder': 'Escribe Nombres y Apellidos/Razón Social', 'rows': 3, 'style': 'width: 400px;'}),
            'cedula_representante': forms.TextInput(attrs={'placeholder': 'Escribe Cédula Representante', 'style': 'width: 250px;'}),
            'nombres_representante': forms.TextInput(attrs={'placeholder': 'Escribe Nombres Representante', 'style': 'width: 400px;'}),
            # AQUÍ ESTÁ EL CAMBIO:
            'direccion': forms.Textarea(attrs={'placeholder': 'Escribe Dirección', 'rows': 3, 'style': 'width: 400px;'}),
            'telefonos': forms.Textarea(attrs={'placeholder': 'Escribe teléfonos', 'rows': 3, 'style': 'width: 400px;'}),
            'observaciones': forms.Textarea(attrs={'placeholder': 'Escribe la observación', 'rows': 3, 'style': 'width: 400px;'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['imagen'].required = False
        # Accede a la instancia del modelo si existe
        instance = getattr(self, 'instance', None)
        if instance and instance.ced_proveedor:
            # Si codigo tiene valor, hacer el campo readonly
            self.fields['ced_proveedor'].widget.attrs['readonly'] = 'readonly'
            self.fields['nombres_apellidos'].widget.attrs['autofocus'] = 'True'
        else:
            self.fields['ced_proveedor'].widget.attrs['autofocus'] = 'True'
