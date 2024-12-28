# products/forms.py
from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['producto_id', 'nombre', 'descripcion', 'cantidad', 'precio_compra', 'precio_venta', 'codigo_barras']
        widgets = {
            'producto_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ID único del producto'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_compra': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control'}),
            'codigo_barras': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_producto_id(self):
        producto_id = self.cleaned_data.get('producto_id')
        if Product.objects.filter(producto_id=producto_id).exists():
            raise forms.ValidationError("El ID del producto debe ser único.")
        return producto_id
