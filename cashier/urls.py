#cashier/views.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.cashier_dashboard, name='cashier_dashboard'),
    path('abrir-caja/', views.abrir_caja, name='abrir_caja'),
    path('cerrar-caja/', views.cerrar_caja, name='cerrar_caja'),
    path('buscar-producto/', views.buscar_producto, name='buscar_producto'),
    path('ajustar-cantidad/', views.ajustar_cantidad, name='ajustar_cantidad'),
    path('agregar-al-carrito/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('listar-carrito/', views.listar_carrito, name='listar_carrito'),
    path('limpiar-carrito/', views.limpiar_carrito, name='limpiar_carrito'),
]
