Sistema POS (MOV-OS)
MOV-OS es un sistema de punto de venta (POS) desarrollado en Django para la gestión de ventas, manejo de inventario y control de caja. Este proyecto incluye funcionalidades como apertura y cierre de caja, búsqueda de productos, control de carrito de compras, generación de reportes y gestión de transacciones.

Requisitos
Antes de instalar y ejecutar el sistema, asegúrate de contar con lo siguiente:

Python 3.8 o superior.
Django 4.2 o superior.
Una base de datos compatible (SQLite, PostgreSQL, MySQL, etc.).
Node.js y npm (opcional, para compilación de estilos o scripts avanzados).
Git (opcional, para clonar el repositorio).
Instalación
Sigue los pasos para instalar y ejecutar el sistema:

Clona el repositorio: git clone https://github.com/usuario/sistema-pos.git cd sistema-pos

Crea un entorno virtual e instálalo: python -m venv venv source venv/bin/activate (En Windows: venv\Scripts\activate)

Instala las dependencias: pip install -r requirements.txt

Realiza las migraciones de la base de datos: python manage.py makemigrations python manage.py migrate

Crea un superusuario para acceder al sistema: python manage.py createsuperuser

Inicia el servidor de desarrollo: python manage.py runserver

Accede al sistema desde: http://127.0.0.1:8000/

Uso
Apertura de Caja
Registra los datos iniciales como efectivo inicial para comenzar a realizar ventas.

Gestión de Productos
Utiliza la barra de búsqueda para encontrar productos por nombre o código de barras.

Carrito de Compras
Agrega, ajusta o elimina productos en el carrito. El sistema calcula automáticamente el total de la venta y el vuelto.

Confirmar Venta
Selecciona el tipo de venta (boleta o factura) y la forma de pago (efectivo, débito o crédito). Confirma la venta para generar un reporte.

Cierre de Caja
Calcula los totales y registra el estado final de la caja.

Estructura del Proyecto
cashier/: Contiene las vistas, modelos y URLs del sistema POS.
templates/cashier/: Plantillas HTML.
static/cashier/: Archivos CSS y JavaScript personalizados.
manage.py: Script principal del proyecto.
requirements.txt: Lista de dependencias.
Modelos de Base de Datos
1. AperturaCierreCaja
Campos:

usuario: Relación al usuario.
efectivo_inicial: DecimalField.
efectivo_final: DecimalField.
ventas_totales: DecimalField.
fecha_apertura: DateTimeField.
fecha_cierre: DateTimeField.
2. Producto
Campos:

nombre: CharField.
codigo: CharField.
precio_venta: DecimalField.
stock: IntegerField.
3. Venta
Campos:

empleado: Relación al usuario.
tipo_venta: CharField.
forma_pago: CharField.
total: DecimalField.
fecha: DateTimeField.
4. VentaDetalle
Campos:

venta: ForeignKey a Venta.
producto: ForeignKey a Producto.
cantidad: IntegerField.
precio_unitario: DecimalField.
Comandos Útiles
Instalar dependencias
pip install -r requirements.txt

Realizar migraciones
python manage.py makemigrations
python manage.py migrate

Crear superusuario
python manage.py createsuperuser

Iniciar el servidor
python manage.py runserver

Resetear la base de datos (opcional)
python manage.py flush

Funcionalidades Principales
Apertura y Cierre de Caja
Manejo completo del flujo de efectivo inicial y final.

Gestión de Productos
Búsqueda avanzada y control de inventario.

Carrito de Compras
Dinámica de selección, ajuste y eliminación de productos.

Ventas
Procesamiento de ventas con múltiples tipos y formas de pago.

Reportes
Generación automática de reportes después de cada venta.

Seguridad
Sistema protegido con autenticación de usuarios y protección CSRF.


