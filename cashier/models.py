#cashier/models.py
from django.conf import settings  # Asegúrate de importar settings
from django.db import models
from products.models import Product
from django.contrib.auth import get_user_model

class Venta(models.Model):
    empleado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_venta = models.CharField(
        max_length=20,
        choices=[('boleta', 'Boleta Electrónica'), ('factura', 'Factura Electrónica')],
        default='boleta'
    )
    forma_pago = models.CharField(
        max_length=20,
        choices=[('efectivo', 'Efectivo'), ('debito', 'Tarjeta de Débito'), ('credito', 'Tarjeta de Crédito')],
        default='efectivo'
    )

    def __str__(self):
        return f"Venta #{self.id} - Total: ${self.total}"

class VentaDetalle(models.Model):
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ventadetalles_cashier')
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)


    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario



User = get_user_model()

class AperturaCierreCaja(models.Model):
    ESTADO_CAJA = [
        ('abierta', 'Abierta'),
        ('cerrada', 'Cerrada'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Cajero Responsable")
    fecha_apertura = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y Hora de Apertura")
    fecha_cierre = models.DateTimeField(null=True, blank=True, verbose_name="Fecha y Hora de Cierre")
    efectivo_inicial = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Efectivo Inicial (Caja Chica)")
    total_ventas_efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Total Ventas en Efectivo")
    total_ventas_credito = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Total Ventas con Tarjeta de Crédito")
    total_ventas_debito = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, verbose_name="Total Ventas con Tarjeta de Débito")
    estado = models.CharField(max_length=10, choices=ESTADO_CAJA, default='abierta', verbose_name="Estado de la Caja")

    class Meta:
        verbose_name = "Apertura y Cierre de Caja"
        verbose_name_plural = "Aperturas y Cierres de Caja"

    def __str__(self):
        return f"Caja {self.estado.capitalize()} - {self.usuario.username} - {self.fecha_apertura.strftime('%d-%m-%Y %H:%M')}"

