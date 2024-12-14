#products/models.py
from django.db import models

class Product(models.Model):
    nombre = models.CharField(max_length=255)  # Nombre del producto
    codigo_barras = models.CharField(max_length=50, unique=True, null=True, blank=True)  # Código de barras
    descripcion = models.TextField(null=True, blank=True)  # Descripción del producto
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Precio de compra
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)  # Precio de venta
    cantidad = models.IntegerField(default=0)  # Cantidad (puedes usarlo como stock inicial o equivalente)
    stock = models.IntegerField(default=0)  # Stock del producto

    def __str__(self):
        return self.nombre
