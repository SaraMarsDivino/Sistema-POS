#reports/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from cashier.models import Venta, AperturaCierreCaja
from auth_app.models import User  # Modelo de usuario personalizado


@login_required
def report_dashboard(request):
    """Pantalla principal para la generación de reportes"""
    return render(request, 'reports/report_dashboard.html')


@login_required
def sales_dashboard(request):
    """Pantalla principal de Gestión de Ventas con opciones"""
    return render(request, 'reports/sales_dashboard.html')


@login_required
def sales_history(request):
    """Historial de Ventas"""
    # Obtener parámetros de filtrado desde GET
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    empleado_id = request.GET.get('empleado')  # ID del empleado
    page = request.GET.get('page', 1)

    # Obtener todas las ventas y ordenar por fecha descendente
    ventas = Venta.objects.all().order_by('-fecha')

    # Filtrar por rango de fechas si se proporcionan
    if fecha_inicio and fecha_fin:
        try:
            fecha_inicio = parse_date(fecha_inicio)
            fecha_fin = parse_date(fecha_fin)
            ventas = ventas.filter(fecha__range=[fecha_inicio, fecha_fin])
        except ValueError:
            ventas = Venta.objects.none()  # Manejar valores de fecha inválidos con una consulta vacía

    # Filtrar por empleado si se selecciona
    if empleado_id:
        try:
            empleado_id = int(empleado_id)
            ventas = ventas.filter(empleado_id=empleado_id)
        except ValueError:
            ventas = Venta.objects.none()  # Manejar valores de empleado inválidos con una consulta vacía

    # Configuración de la paginación
    paginator = Paginator(ventas, 8)  # 8 ventas por página
    sales_page = paginator.get_page(page)

    # Obtener la lista de empleados para el selector de filtrado
    empleados = User.objects.all()

    return render(request, 'reports/sales_history.html', {
        'sales': sales_page,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'empleado_id': empleado_id if empleado_id else None,
        'empleados': empleados,
    })


@login_required
def cash_history(request):
    """Historial de Caja"""
    # Obtener todas las aperturas/cierres de caja y ordenar por fecha de apertura descendente
    cajas = AperturaCierreCaja.objects.all().order_by('-fecha_apertura')

    # Configuración de la paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(cajas, 5)  # 5 registros de caja por página
    cash_page = paginator.get_page(page)

    # Calcular datos adicionales para cada caja
    for caja in cash_page:
        if caja.estado == 'cerrada':
            caja.vuelto_entregado = caja.vuelto_entregado or 0  # Validar vuelto entregado
            caja.efectivo_final = caja.efectivo_final or (
                caja.efectivo_inicial + caja.total_ventas_efectivo - caja.vuelto_entregado
            )

    return render(request, 'reports/cash_history.html', {
        'cajas': cash_page
    })




@login_required
def sales_report(request, sale_id):
    """Reporte detallado de una venta específica"""
    try:
        sale = get_object_or_404(Venta, id=sale_id)
        details = sale.detalles.all()
        return render(request, 'reports/sales_report.html', {'sale': sale, 'details': details})
    except Exception as e:
        return render(request, 'reports/sales_report.html', {
            'error': str(e),
            'sale': None,
            'details': None
        })
