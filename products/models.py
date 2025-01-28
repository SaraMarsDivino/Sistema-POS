# products/models.py
from django.db import models

class Product(models.Model):
    producto_id = models.CharField(max_length=20, unique=True, default="default_id")  # ID único del producto
    nombre = models.CharField(max_length=255)  # Nombre del producto
    codigo_barras = models.CharField(max_length=50, unique=True, null=True, blank=True)  # Código de barras
    descripcion = models.TextField(null=True, blank=True)  # Descripción del producto
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Precio de compra
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)  # Precio de venta
    cantidad = models.IntegerField(default=0)  # Cantidad
    stock = models.IntegerField(default=0)  # Stock del producto
    permitir_venta_sin_stock = models.BooleanField(default=False)  # Permitir venta sin stock

    def __str__(self):
        return f"{self.producto_id} - {self.nombre}"
