Sistema POS (MOV-OS)
MOV-OS es un sistema de punto de venta (POS) desarrollado en Django para la gestión de ventas, manejo de inventario y control de caja. Este proyecto incluye funcionalidades como apertura y cierre de caja, búsqueda de productos, control de carrito de compras, generación de reportes y gestión de transacciones.

Índice
Requisitos
Instalación
Uso
Estructura del Proyecto
Funcionalidades Principales
Capturas de Pantalla
Contribución
Licencia
Requisitos
Antes de instalar y ejecutar el sistema, asegúrate de contar con los siguientes requisitos:

Python 3.8 o superior
Django 4.2 o superior
Base de datos compatible (SQLite, PostgreSQL, MySQL, etc.)
Node.js y npm (opcional, para compilación de estilos o scripts avanzados)
Git (opcional, para clonar el repositorio)
Instalación
Sigue los pasos a continuación para instalar y ejecutar el sistema:

Clona el repositorio desde GitHub y accede al directorio del proyecto.
Crea un entorno virtual para instalar las dependencias necesarias.
Instala las dependencias listadas en el archivo requirements.txt.
Configura la base de datos en el archivo settings.py.
Aplica las migraciones de Django para inicializar la base de datos.
(Opcional) Carga datos iniciales, si corresponde.
Inicia el servidor de desarrollo con el comando de Django.
Accede al sistema a través de la URL proporcionada, usualmente http://127.0.0.1:8000.
Uso
Apertura de Caja
Accede a la sección de apertura de caja y registra los datos iniciales para comenzar a realizar transacciones.

Gestión de Productos
Utiliza la barra de búsqueda para encontrar productos por nombre o código de barras. Agrega productos al carrito directamente desde los resultados de la búsqueda.

Carrito de Compras
Agrega, ajusta o elimina productos desde el carrito de compras. El sistema calcula automáticamente el total de la venta y el vuelto, si corresponde.

Confirmar Venta
Selecciona el tipo de venta (boleta o factura) y la forma de pago (efectivo, débito o crédito). Confirma la venta y genera un reporte automáticamente.

Cierre de Caja
Desde la página principal, utiliza el botón de cierre de caja para calcular totales de ventas y registrar el estado final de la caja.

Estructura del Proyecto
cashier/: Contiene las vistas, modelos y URLs relacionadas con las operaciones del POS.
templates/cashier/: Contiene las plantillas HTML utilizadas para las vistas del POS.
static/cashier/: Contiene los archivos CSS y JavaScript personalizados.
manage.py: Script principal para la administración del proyecto.
requirements.txt: Lista de dependencias del proyecto.
Funcionalidades Principales
Apertura y Cierre de Caja: Manejo completo del flujo de efectivo inicial y final.
Gestión de Productos: Búsqueda avanzada y control de inventario.
Carrito de Compras: Dinámica de selección, ajuste y eliminación de productos.
Ventas: Procesamiento de ventas con múltiples tipos y formas de pago.
Reportes: Generación de reportes automáticos después de cada venta.
Seguridad: Sistema protegido con autenticación de usuarios y tokens CSRF.
Capturas de Pantalla
Página de Caja
Visualización de las funciones principales de caja.
Reportes de Ventas
Vista detallada de reportes generados automáticamente después de cada venta.
Contribución
Si deseas contribuir al proyecto, realiza un fork del repositorio, crea una rama para tu funcionalidad, realiza los cambios necesarios y abre un Pull Request.
