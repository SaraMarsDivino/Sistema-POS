# Generated by Django 5.0.7 on 2024-12-19 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cashier', '0008_aperturacierrecaja_ventas_totales'),
    ]

    operations = [
        migrations.AddField(
            model_name='aperturacierrecaja',
            name='vuelto_entregado',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Total Vuelto Entregado'),
        ),
    ]
