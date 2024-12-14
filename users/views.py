# users/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from auth_app.models import User
from .forms import UserForm  # Asegura que UserForm esté configurado con los campos necesarios


@login_required
def home(request):
    # Redirige a la vista según si el usuario es admin o cajero
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    else:
        return redirect('cashier_dashboard')

@login_required
def admin_dashboard(request):
    return render(request, 'users/admin_dashboard.html')

@login_required
def cashier_dashboard(request):
    return render(request, 'cashier/dashboard.html')  # Vista de cajero

def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')  # Redirige a `home` para lógica de roles
        else:
            return render(request, 'users/login.html', {'error': 'Credenciales incorrectas'})
    return render(request, 'users/login.html')

@login_required
def profile(request):
    return render(request, 'users/profile.html', {'user': request.user})

def custom_logout(request):
    logout(request)
    return redirect('login')

@login_required
def user_management(request):
    # Vista de gestión de usuarios
    users = User.objects.all()
    return render(request, 'users/user_management.html', {'users': users})

@login_required
def create_user(request):
    # Vista para crear un nuevo usuario
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])  # Encripta la contraseña
            user.save()
            return redirect('user_management')
    else:
        form = UserForm()
    return render(request, 'users/create_user.html', {'form': form})

@login_required
def edit_user(request, user_id):
    # Vista para editar un usuario existente
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_management')
    else:
        form = UserForm(instance=user)
    return render(request, 'users/edit_user.html', {'form': form, 'user': user})

@login_required
def delete_user(request, user_id):
    # Vista para eliminar un usuario
    user = get_object_or_404(User, id=user_id)
    print(user)
    if request.method == 'POST':
        user.delete()
        return redirect('user_management')
    return render(request, 'users/delete_user.html', {'user': user})



@login_required
def create_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])  # Hasheamos la contraseña
            user.save()
            return redirect('user_management')  # Redirige a la vista de gestión de usuarios después de crear el usuario
    else:
        form = UserForm()
    return render(request, 'users/create_user.html', {'form': form})

def create_user(request):
    # Vista para crear un nuevo usuario
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])  # Encripta la contraseña
            user.save()
            return redirect('user_management')
    else:
        form = UserForm()
    return render(request, 'users/create_user.html', {'form': form})