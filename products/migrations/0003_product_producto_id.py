# Generated by Django 5.0.7 on 2024-12-26 23:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_product_stock_alter_product_cantidad_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='producto_id',
            field=models.CharField(default='default_id', max_length=20, unique=True),
        ),
    ]