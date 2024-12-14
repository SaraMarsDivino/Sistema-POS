#views.py/products
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q  # Para filtros de búsqueda
from .models import Product
from .forms import ProductForm
from django.contrib import messages

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
