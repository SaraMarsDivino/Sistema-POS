#cashier/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction
from .models import Venta, VentaDetalle
from products.models import Product
from django.urls import reverse
import json
from django.contrib import messages
from .models import AperturaCierreCaja
from .forms import AperturaCajaForm
from django.db import models

@login_required
def abrir_caja(request):
    # Verificar si ya existe una caja abierta para el usuario actual
    caja_abierta = AperturaCierreCaja.objects.filter(usuario=request.user, estado='abierta').first()
    if caja_abierta:
        messages.info(request, "Ya tienes una caja abierta.")
        return redirect('cashier_dashboard')

    if request.method == 'POST':
        form = AperturaCajaForm(request.POST)
        if form.is_valid():
            caja = form.save(commit=False)
            caja.usuario = request.user
            caja.estado = 'abierta'
            caja.save()
            messages.success(request, "Caja abierta exitosamente.")
            return redirect('cashier_dashboard')
    else:
        form = AperturaCajaForm()

    return render(request, 'cashier/abrir_caja.html', {'form': form})

@login_required
def cerrar_caja(request):
    # Verificar si el usuario tiene una caja abierta
    caja_abierta = AperturaCierreCaja.objects.filter(usuario=request.user, estado='abierta').first()
    if not caja_abierta:
        messages.warning(request, "No tienes una caja abierta para cerrar.")
        return redirect('cashier_dashboard')

    if request.method == 'POST':
        # Calcular el total de ventas realizadas
        ventas_del_dia = Venta.objects.filter(empleado=request.user, fecha__gte=caja_abierta.fecha_apertura)
        total_ventas = ventas_del_dia.aggregate(total=models.Sum('total'))['total'] or 0

        # Calcular efectivo esperado
        efectivo_esperado = caja_abierta.efectivo_inicial + total_ventas
        caja_abierta.ventas_totales = total_ventas
        caja_abierta.efectivo_final = efectivo_esperado
        caja_abierta.estado = 'cerrada'
        caja_abierta.save()

        messages.success(request, f"Caja cerrada exitosamente. Total en caja: ${efectivo_esperado:.2f}.")
        return redirect('cashier_dashboard')

    return render(request, 'cashier/cerrar_caja.html', {'caja_abierta': caja_abierta})

@transaction.atomic
@login_required
def cashier_dashboard(request):
    # Verificar si el usuario tiene una caja abierta
    caja_abierta = AperturaCierreCaja.objects.filter(usuario=request.user, estado='abierta').first()
    if not caja_abierta:
        messages.warning(request, "Debes abrir una caja para acceder.")
        return redirect('abrir_caja')

    if request.method == 'GET':
        productos = Product.objects.all()
        return render(request, 'cashier/cashier.html', {'productos': productos, 'caja_abierta': caja_abierta})
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Obtener datos como JSON
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
                    producto = Product.objects.get(id=item['producto_id'])
                    cantidad = int(item['cantidad'])

                    if producto.stock < cantidad:
                        return JsonResponse(
                            {"error": f"El producto '{producto.nombre}' no tiene suficiente stock."},
                            status=400
                        )

                    producto.stock -= cantidad
                    producto.save()

                    detalle = VentaDetalle.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=producto.precio_venta
                    )
                    total += detalle.cantidad * detalle.precio_unitario

                venta.total = total
                venta.save()

            return JsonResponse({"success": True, "mensaje": "Compra confirmada con éxito."})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Error en el formato de los datos enviados."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    elif request.method == 'GET':
        productos = Product.objects.all()
        return render(request, 'cashier/cashier.html', {'productos': productos})

    return JsonResponse({"error": "Método no permitido."}, status=405)

@login_required
def finalizar_venta(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    detalles = venta.detalles.all()
    return render(request, 'cashier/resumen.html', {'venta': venta, 'detalles': detalles})

@login_required
def buscar_producto(request):
    query = request.GET.get('q', '').strip()
    productos = Product.objects.filter(name__icontains=query) | Product.objects.filter(barcode__icontains=query)
    resultados = [
        {'id': producto.id, 'nombre': producto.name, 'precio_venta': str(producto.price)}
        for producto in productos
    ]
    return JsonResponse({'productos': resultados})

@login_required
def ajustar_cantidad(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            producto_id = int(data.get('producto_id'))
            cambio_cantidad = int(data.get('cantidad'))

            # Obtener el producto
            producto = get_object_or_404(Product, id=producto_id)

            # Validar stock (solo para incremento)
            if cambio_cantidad > 0 and producto.stock < cambio_cantidad:
                return JsonResponse({"error": f"Stock insuficiente para el producto '{producto.nombre}'."}, status=400)

            # Actualizar el carrito
            carrito = request.session.get('carrito', [])
            for item in carrito:
                if item['producto_id'] == producto_id:
                    item['cantidad'] += cambio_cantidad
                    if item['cantidad'] <= 0:
                        carrito.remove(item)  # Eliminar del carrito si la cantidad es 0
                    break
            else:
                return JsonResponse({"error": "Producto no encontrado en el carrito."}, status=404)

            request.session['carrito'] = carrito
            request.session.modified = True

            return JsonResponse({"mensaje": "Cantidad ajustada correctamente.", "carrito": carrito})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido."}, status=405)

@login_required
def agregar_al_carrito(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Datos inválidos."}, status=400)

        producto_id = data.get("producto_id")
        cantidad = int(data.get("cantidad", 1))

        producto = get_object_or_404(Product, id=producto_id)

        # Validar stock antes de agregar
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
                'nombre': producto.name,
                'precio': producto.price,
                'cantidad': cantidad,
            })

        request.session['carrito'] = carrito
        request.session.modified = True

        return JsonResponse({'mensaje': 'Producto agregado al carrito', 'carrito': carrito})

    return JsonResponse({'error': 'Método no permitido'}, status=405)

@login_required
def listar_carrito(request):
    carrito = request.session.get('carrito', [])
    return JsonResponse({'carrito': carrito})

@login_required
def limpiar_carrito(request):
    request.session['carrito'] = []
    request.session.modified = True
    return JsonResponse({'mensaje': 'Carrito limpio con éxito'})

@login_required
def buscar_producto(request):
    query = request.GET.get('q', '').strip()
    productos = Product.objects.filter(nombre__icontains=query) | Product.objects.filter(codigo_barras__icontains=query)
    resultados = [
        {'id': producto.id, 'nombre': producto.nombre, 'precio_venta': str(producto.precio_venta)}
        for producto in productos
    ]
    return JsonResponse({'productos': resultados})

