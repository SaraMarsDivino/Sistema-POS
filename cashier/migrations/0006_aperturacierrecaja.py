# Generated by Django 5.0.7 on 2024-11-28 20:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cashier', '0005_venta_forma_pago_venta_tipo_venta_alter_venta_total'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AperturaCierreCaja',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_apertura', models.DateTimeField(auto_now_add=True, verbose_name='Fecha y Hora de Apertura')),
                ('fecha_cierre', models.DateTimeField(blank=True, null=True, verbose_name='Fecha y Hora de Cierre')),
                ('efectivo_inicial', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Efectivo Inicial (Caja Chica)')),
                ('total_ventas_efectivo', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Total Ventas en Efectivo')),
                ('total_ventas_credito', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Total Ventas con Tarjeta de Crédito')),
                ('total_ventas_debito', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Total Ventas con Tarjeta de Débito')),
                ('estado', models.CharField(choices=[('abierta', 'Abierta'), ('cerrada', 'Cerrada')], default='abierta', max_length=10, verbose_name='Estado de la Caja')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Cajero Responsable')),
            ],
            options={
                'verbose_name': 'Apertura y Cierre de Caja',
                'verbose_name_plural': 'Aperturas y Cierres de Caja',
            },
        ),
    ]
