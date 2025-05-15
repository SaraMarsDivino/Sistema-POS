from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_dashboard, name='report_dashboard'),
    path('sales/dashboard/', views.sales_dashboard, name='sales_dashboard'),  # Nueva pantalla inicial
    path('sales/history/', views.sales_history, name='sales_history'),  # Historial de ventas
    path('sales/<int:sale_id>/', views.sales_report, name='sales_report'),  # Reporte detallado
    path('cash/history/', views.cash_history, name='cash_history'),  # Historial de caja
]
