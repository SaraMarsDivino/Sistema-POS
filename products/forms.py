# products/forms.py
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'producto_id', 'nombre', 'descripcion', 'cantidad',
            'precio_compra', 'precio_venta', 'codigo_barras', 'permitir_venta_sin_stock'
        ]
        widgets = {
            'producto_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID único del producto'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control'}),
            'codigo_barras': forms.TextInput(attrs={'class': 'form-control'}),
            'permitir_venta_sin_stock': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

    def clean_producto_id(self):
        producto_id = self.cleaned_data.get('producto_id')
        qs = Product.objects.filter(producto_id=producto_id)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("El ID del producto debe ser único.")
        return producto_id
