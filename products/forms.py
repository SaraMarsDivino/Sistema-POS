from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['nombre', 'descripcion', 'precio_venta', 'codigo_barras', 'stock']
