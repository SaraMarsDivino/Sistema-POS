from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction, models
from django.urls import reverse
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
import json

from .models import Venta, VentaDetalle, AperturaCierreCaja
from products.models import Product
from .forms import AperturaCajaForm


# 📌 ABRIR CAJA
@login_required
def abrir_caja(request):
    """Verifica si ya hay una caja abierta. Si no, abre una nueva con el monto inicial."""
    caja_abierta = AperturaCierreCaja.objects.filter(usuario=request.user, estado='abierta').first()
    
    if caja_abierta:
        messages.info(request, "Ya tienes una caja abierta.")
        return redirect('cashier_dashboard')

    if request.method == 'POST':
        efectivo_inicial = float(request.POST.get('efectivo_inicial', 0))
        AperturaCierreCaja.objects.create(
            usuario=request.user,
            efectivo_inicial=efectivo_inicial,
            estado='abierta'
        )
        messages.success(request, f"Caja abierta con éxito. Monto inicial: ${efectivo_inicial:,.2f}")
        return redirect('cashier_dashboard')

    return render(request, 'cashier/abrir_caja.html')


# 📌 DASHBOARD DEL CAJERO
# 📌 DASHBOARD DEL CAJERO
@transaction.atomic
@login_required
def cashier_dashboard(request):
    caja_abierta = AperturaCierreCaja.objects.filter(usuario=request.user, estado='abierta').first()

    if not caja_abierta:
        messages.warning(request, "No tienes una caja abierta. Debes abrir una caja para realizar ventas.")
        return redirect('abrir_caja')

    if request.method == 'GET':
        productos = Product.objects.all()
        return render(request, 'cashier/cashier.html', {
            'productos': productos,
            'caja_abierta': caja_abierta
        })

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            carrito = data.get('carrito', [])
            tipo_venta = data.get('tipo_venta', 'boleta')
            forma_pago = data.get('forma_pago', 'efectivo')
            cliente_paga = float(data.get('cliente_paga', 0))

            if not carrito:
                return JsonResponse({"error": "El carrito está vacío."}, status=400)

            with transaction.atomic():
                venta = Venta.objects.create(
                    empleado=request.user,
                    tipo_venta=tipo_venta,
                    forma_pago=forma_pago,
                    total=0
                )

                total = 0
                for item in carrito:
                    producto_id = item.get('producto_id')
                    if not producto_id:
                        return JsonResponse({"error": "Falta el producto_id en el carrito."}, status=400)

                    producto = get_object_or_404(Product, id=producto_id)
                    cantidad = int(item.get('cantidad', 1))

                    if not producto.permitir_venta_sin_stock and producto.stock < cantidad:
                        return JsonResponse(
                            {"error": f"El producto '{producto.nombre}' no tiene suficiente stock."},
                            status=400
                        )

                    producto.stock -= cantidad
                    producto.save()

                    VentaDetalle.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=producto.precio_venta
                    )

                    total += cantidad * producto.precio_venta

                venta.total = total
                venta.save()

            reporte_url = reverse('reporte_venta', args=[venta.id])
            return JsonResponse({
                "success": True,
                "mensaje": "Compra confirmada con éxito.",
                "reporte_url": reporte_url
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Error en los datos enviados."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido."}, status=405)




# 📌 PROCESAR UNA VENTA
@login_required
def procesar_venta(request):
    """Procesa la venta y actualiza el stock del producto."""
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido."}, status=405)

    try:
        data = json.loads(request.body)
        carrito = data.get('carrito', [])
        tipo_venta = data.get('tipo_venta', 'boleta')
        forma_pago = data.get('forma_pago', 'efectivo')
        cliente_paga = float(data.get('cliente_paga', 0))

        if not carrito:
            return JsonResponse({"error": "El carrito está vacío."}, status=400)

        with transaction.atomic():
            venta = Venta.objects.create(
                empleado=request.user,
                tipo_venta=tipo_venta,
                forma_pago=forma_pago,
                total=0
            )

            total = 0
            for item in carrito:
                producto = get_object_or_404(Product, id=item.get('producto_id'))
                cantidad = int(item.get('cantidad', 1))

                if not producto.permitir_venta_sin_stock and producto.stock < cantidad:
                    return JsonResponse({"error": f"Stock insuficiente para '{producto.nombre}'."}, status=400)

                if producto.stock >= cantidad:
                    producto.stock -= cantidad
                    producto.save()

                VentaDetalle.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=producto.precio_venta
                )
                total += cantidad * producto.precio_venta

            venta.total = total
            venta.save()

        reporte_url = reverse('sales_report', args=[venta.id])
        return JsonResponse({"success": True, "mensaje": "Compra confirmada con éxito.", "reporte_url": reporte_url})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Error en el formato de los datos enviados."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



# 📌 CERRAR CAJA - CORREGIDO
@login_required
def cerrar_caja(request):
    caja_abierta = AperturaCierreCaja.objects.filter(usuario=request.user, estado='abierta').first()
    if not caja_abierta:
        return JsonResponse({"error": "No tienes una caja abierta para cerrar."}, status=403)

    # 📊 Obtener ventas del día
    ventas_del_dia = Venta.objects.filter(empleado=request.user, fecha__gte=caja_abierta.fecha_apertura)

    # 📊 Calcular totales asegurando que solo afecten los montos correctos
    total_ventas = ventas_del_dia.aggregate(total=models.Sum('total'))['total'] or 0
    total_efectivo = ventas_del_dia.filter(forma_pago='efectivo').aggregate(total=models.Sum('total'))['total'] or 0
    total_credito = ventas_del_dia.filter(forma_pago='credito').aggregate(total=models.Sum('total'))['total'] or 0
    total_debito = ventas_del_dia.filter(forma_pago='debito').aggregate(total=models.Sum('total'))['total'] or 0
    vuelto_entregado = ventas_del_dia.filter(forma_pago='efectivo').aggregate(total=models.Sum('vuelto_entregado'))['total'] or 0

    # 📌 Calcular efectivo final (NO incluir pagos con tarjeta)
    efectivo_final = caja_abierta.efectivo_inicial + total_efectivo - vuelto_entregado

    if request.method == 'POST':
        caja_abierta.ventas_totales = total_ventas
        caja_abierta.total_ventas_efectivo = total_efectivo  # ✅ Solo pagos en efectivo
        caja_abierta.total_ventas_credito = total_credito    # ✅ Solo pagos con crédito
        caja_abierta.total_ventas_debito = total_debito      # ✅ Solo pagos con débito
        caja_abierta.vuelto_entregado = vuelto_entregado
        caja_abierta.efectivo_final = efectivo_final  # ✅ No debe incluir ventas con tarjeta
        caja_abierta.estado = 'cerrada'
        caja_abierta.fecha_cierre = timezone.now()
        caja_abierta.save()

        return JsonResponse({
            "success": True,
            "mensaje": "Caja cerrada correctamente.",
            "caja_id": caja_abierta.id
        })

    return JsonResponse({"error": "Método no permitido."}, status=405)









# 📌 DETALLE DE CIERRE DE CAJA - CORREGIDO
@login_required
def detalle_caja(request, caja_id):
    """Muestra el resumen de la caja cerrada en el orden correcto."""
    caja = get_object_or_404(AperturaCierreCaja, id=caja_id)

    # 📌 Pasar los valores correctamente al template
    contexto = {
        'caja': caja,
        'efectivo_inicial': caja.efectivo_inicial or 0,
        'total_debito': caja.total_ventas_debito or 0,
        'total_credito': caja.total_ventas_credito or 0,
        'vuelto_entregado': caja.vuelto_entregado or 0,
        'efectivo_final': caja.efectivo_final or caja.efectivo_inicial,  # Asegura que tenga un valor válido
        'total_ventas': caja.ventas_totales or 0
        
    }

    return render(request, 'cashier/detalle_caja.html', contexto)




# 📌 HISTORIAL DE CAJAS
@login_required
def historial_caja(request):
    """Lista todas las cajas abiertas/cerradas."""
    historial_cajas = AperturaCierreCaja.objects.all().order_by('-fecha_apertura')
    return render(request, 'cashier/historial_caja.html', {'historial_cajas': historial_cajas})


# 📌 BUSCAR PRODUCTO
@login_required
def buscar_producto(request):
    """Busca productos por nombre o código de barras."""
    query = request.GET.get('q', '').strip()
    productos = Product.objects.filter(Q(nombre__icontains=query) | Q(codigo_barras__icontains=query)) if query else []
    resultados = [{'id': p.id, 'nombre': p.nombre, 'precio_venta': str(p.precio_venta)} for p in productos]
    return JsonResponse({'productos': resultados})


# 📌 REPORTE DE VENTA
@login_required
def reporte_venta(request, venta_id):
    """Muestra el detalle de una venta específica."""
    venta = get_object_or_404(Venta, id=venta_id)
    detalles = venta.detalles.all()
    return render(request, 'cashier/reporte_venta.html', {'venta': venta, 'detalles': detalles})

# 📌 AJUSTAR CANTIDAD EN EL CARRITO
@login_required
def ajustar_cantidad(request):
    """Ajusta la cantidad de un producto en el carrito de compras."""
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido."}, status=405)

    try:
        data = json.loads(request.body)
        producto_id = int(data.get('producto_id'))
        cambio_cantidad = int(data.get('cantidad'))

        producto = get_object_or_404(Product, id=producto_id)

        # Verificar si hay stock suficiente antes de incrementar
        if cambio_cantidad > 0 and producto.stock < cambio_cantidad:
            return JsonResponse({"error": f"Stock insuficiente para '{producto.nombre}'."}, status=400)

        # Obtener el carrito de la sesión
        carrito = request.session.get('carrito', [])
        for item in carrito:
            if item['producto_id'] == producto_id:
                item['cantidad'] += cambio_cantidad
                if item['cantidad'] <= 0:
                    carrito.remove(item)  # Eliminar si la cantidad llega a 0
                break
        else:
            return JsonResponse({"error": "Producto no encontrado en el carrito."}, status=404)

        request.session['carrito'] = carrito
        request.session.modified = True

        return JsonResponse({"mensaje": "Cantidad ajustada correctamente.", "carrito": carrito})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# 📌 AGREGAR PRODUCTO AL CARRITO
@login_required
def agregar_al_carrito(request):
    """Añade un producto al carrito, verificando stock y caja abierta."""
    caja_abierta = AperturaCierreCaja.objects.filter(usuario=request.user, estado='abierta').first()
    if not caja_abierta:
        return JsonResponse({'error': 'No tienes una caja abierta.'}, status=403)

    if request.method != "POST":
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        producto_id = data.get("producto_id")
        cantidad = int(data.get("cantidad", 1))

        producto = get_object_or_404(Product, id=producto_id)

        if producto.stock < cantidad:
            return JsonResponse({"error": "Stock insuficiente para este producto."}, status=400)

        carrito = request.session.get('carrito', [])

        for item in carrito:
            if item['producto_id'] == producto.id:
                item['cantidad'] += cantidad
                break
        else:
            carrito.append({
                'producto_id': producto.id,
                'nombre': producto.nombre,
                'precio': producto.precio_venta,
                'cantidad': cantidad,
            })

        request.session['carrito'] = carrito
        request.session.modified = True

        return JsonResponse({'mensaje': 'Producto agregado al carrito', 'carrito': carrito})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# 📌 LISTAR PRODUCTOS DEL CARRITO
@login_required
def listar_carrito(request):
    """Devuelve el contenido del carrito actual."""
    carrito = request.session.get('carrito', [])
    return JsonResponse({'carrito': carrito})


# 📌 LIMPIAR EL CARRITO
@login_required
def limpiar_carrito(request):
    """Elimina todos los productos del carrito."""
    request.session['carrito'] = []
    request.session.modified = True
    return JsonResponse({'mensaje': 'Carrito limpio con éxito'})
