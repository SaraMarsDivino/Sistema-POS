#views.py/products
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q  # Para filtros de búsqueda
from .models import Product
from .forms import ProductForm
from django.contrib import messages
from django.http import HttpResponse
from openpyxl import Workbook, load_workbook
from .models import Product

def product_management(request):
    # Filtro de búsqueda por nombre
    query = request.GET.get('search', '')
    products = Product.objects.filter(Q(nombre__icontains=query))

    # Paginación
    paginator = Paginator(products, 10)  # 10 productos por página
    page = request.GET.get('page')
    products_page = paginator.get_page(page)

    return render(request, 'products/product_management.html', {
        'products': products_page,
        'search_query': query
    })



def upload_products(request):
    if request.method == 'POST':
        # Verificar si el archivo fue subido
        if 'file' not in request.FILES:
            messages.error(request, 'No se subió ningún archivo.')
            return redirect('upload_products')

        file = request.FILES['file']
        if not file.name.endswith('.xlsx'):
            messages.error(request, 'Por favor sube un archivo válido en formato Excel (.xlsx).')
            return redirect('upload_products')

        # Procesar el archivo Excel
        try:
            workbook = load_workbook(file)
            sheet = workbook.active

            for row in sheet.iter_rows(min_row=2, values_only=True):
                if row[0]:  # Comprobar que la primera columna tenga datos
                    Product.objects.update_or_create(
                        nombre=row[0],
                        defaults={
                            'descripcion': row[1],
                            'cantidad': row[2],
                            'precio_compra': row[3],
                            'precio_venta': row[4],
                            'codigo_barras': row[5]
                        }
                    )
            messages.success(request, 'Productos cargados exitosamente.')
            return redirect('product_management')
        except Exception as e:
            messages.error(request, f'Error procesando el archivo: {str(e)}')
            return redirect('upload_products')

    return render(request, 'products/upload_products.html')

def download_template(request):
    # Crear un archivo Excel como plantilla
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="plantilla_productos.xlsx"'

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Productos'
    headers = ['Nombre', 'Descripción', 'Cantidad', 'Precio de Compra', 'Precio de Venta', 'Código de Barras']
    sheet.append(headers)

    workbook.save(response)
    return response


def create_or_edit_product(request, product_id=None):
    if product_id:
        # Obtener el producto a editar
        product = get_object_or_404(Product, id=product_id)
        form = ProductForm(request.POST or None, instance=product)
        title = 'Editar Producto'
    else:
        # Crear un nuevo producto
        product = None
        form = ProductForm(request.POST or None)
        title = 'Crear Producto'

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto guardado exitosamente.')
            if 'save_and_list' in request.POST:
                return redirect('product_management')
    
    return render(request, 'products/product_form.html', {'form': form, 'title': title, 'product': product})


def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Producto eliminado exitosamente.')
        return redirect('product_management')
    return render(request, 'products/delete_product.html', {'product': product})
