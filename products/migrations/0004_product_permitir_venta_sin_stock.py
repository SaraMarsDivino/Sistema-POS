# Generated by Django 5.0.7 on 2025-01-27 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_product_producto_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='permitir_venta_sin_stock',
            field=models.BooleanField(default=False),
        ),
    ]
