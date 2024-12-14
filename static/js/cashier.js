document.addEventListener("DOMContentLoaded", () => {
    const confirmarCompraButton = document.getElementById("confirmar-compra");
    const cantidadPagadaInput = document.getElementById("cantidad_pagada");
    const vueltoElement = document.getElementById("vuelto");
    const totalPriceElement = document.getElementById("total-price");
    const cartItemsContainer = document.getElementById("cart-items");
    const searchButton = document.getElementById("product-search-button");
    const searchInput = document.getElementById("product-search-input");
    const barcodeInput = document.getElementById("barcode-input");
    const resultsList = document.getElementById("product-search-results");
    let carrito = [];
    let totalCarrito = 0;

    // Restaurar selección desde localStorage
    function restoreSelection(buttonGroup, storageKey) {
        const selectedButtonId = localStorage.getItem(storageKey);
        if (selectedButtonId) {
            toggleButtonGroup(buttonGroup, selectedButtonId, storageKey);
        }
    }

    // Activar un botón de un grupo y guardar selección en localStorage
    function toggleButtonGroup(buttonGroupSelector, selectedButtonId, storageKey) {
        const buttons = document.querySelectorAll(buttonGroupSelector);
        buttons.forEach(button => {
            if (button.id === selectedButtonId) {
                button.classList.add('active');
                localStorage.setItem(storageKey, selectedButtonId);
            } else {
                button.classList.remove('active');
            }
        });
    }

    // Calcular el vuelto
    cantidadPagadaInput.addEventListener("input", () => calcularVuelto());

    function calcularVuelto() {
        const cantidadPagada = parseFloat(cantidadPagadaInput.value) || 0;
        const totalCarrito = parseFloat(totalPriceElement.textContent.replace("$", "")) || 0;
        const vuelto = cantidadPagada - totalCarrito;
        vueltoElement.textContent = `$${vuelto.toFixed(2)}`;
    }

    // Restaurar selecciones de Tipo de Venta y Forma de Pago
    restoreSelection('.btn-group[aria-label="Tipo de Venta"] .btn', 'tipo_venta');
    restoreSelection('.btn-group[aria-label="Forma de Pago"] .btn', 'forma_pago');

    // Configuración de botones para Tipo de Venta
    document.getElementById("boleta").addEventListener("click", () => toggleButtonGroup('.btn-group[aria-label="Tipo de Venta"] .btn', 'boleta', 'tipo_venta'));
    document.getElementById("factura").addEventListener("click", () => toggleButtonGroup('.btn-group[aria-label="Tipo de Venta"] .btn', 'factura', 'tipo_venta'));

    // Configuración de botones para Forma de Pago
    document.getElementById("efectivo").addEventListener("click", () => toggleFormaPago("efectivo"));
    document.getElementById("debito").addEventListener("click", () => toggleFormaPago("debito"));
    document.getElementById("credito").addEventListener("click", () => toggleFormaPago("credito"));

    function toggleFormaPago(metodo) {
        toggleButtonGroup('.btn-group[aria-label="Forma de Pago"] .btn', metodo, 'forma_pago');
        if (metodo === "efectivo") {
            cantidadPagadaInput.value = "";
        } else {
            cantidadPagadaInput.value = totalCarrito.toFixed(2);
        }
        calcularVuelto();
    }

    // Buscar productos
    searchButton.addEventListener("click", async () => {
        const query = searchInput.value.trim();
        if (!query) return alert("Por favor, ingresa un término de búsqueda.");

        try {
            const response = await fetch(`/cashier/buscar-producto/?q=${query}`);
            const data = await response.json();
            resultsList.innerHTML = "";

            if (data.productos.length === 0) {
                resultsList.innerHTML = "<li>No se encontraron productos.</li>";
                return;
            }

            data.productos.forEach(producto => {
                const li = document.createElement("li");
                li.textContent = `${producto.nombre} - $${producto.precio_venta}`;
                const addButton = document.createElement("button");
                addButton.textContent = "+";
                addButton.classList.add("btn", "btn-success", "btn-sm", "ml-2");
                addButton.addEventListener("click", () => agregarAlCarrito(producto.id, producto.nombre, parseFloat(producto.precio_venta)));
                li.appendChild(addButton);
                resultsList.appendChild(li);
            });
        } catch (error) {
            console.error("Error al buscar productos:", error);
            alert("Error al buscar productos.");
        }
    });

    // Event listener para código de barras
    barcodeInput.addEventListener("input", async function () {
        const barcode = this.value.trim();
        if (!barcode) return;

        try {
            const response = await fetch(`/cashier/buscar-producto/?q=${barcode}`);
            const data = await response.json();

            if (data.productos.length === 1) {
                const producto = data.productos[0];
                agregarAlCarrito(producto.id, producto.nombre, parseFloat(producto.precio_venta));
                this.value = ""; // Limpia el campo
            } else {
                alert("Producto no encontrado o múltiples coincidencias.");
            }
        } catch (error) {
            console.error("Error al buscar producto por código de barras:", error);
        }
    });

    // Agregar productos al carrito
    function agregarAlCarrito(productoId, nombre, precio) {
        const productoExistente = carrito.find(item => item.producto_id === productoId);
        if (productoExistente) {
            productoExistente.cantidad += 1;
        } else {
            carrito.push({ producto_id: productoId, nombre, precio, cantidad: 1 });
        }
        actualizarCarrito();
    }

    function actualizarCarrito() {
        cartItemsContainer.innerHTML = "";
        totalCarrito = 0;

        carrito.forEach((item, index) => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${item.cantidad}</td>
                <td>${item.nombre}</td>
                <td>$${(item.cantidad * item.precio).toFixed(2)}</td>
                <td>
                    <button class="btn btn-success btn-sm increment-btn" data-id="${item.producto_id}" data-index="${index}">+</button>
                    <button class="btn btn-danger btn-sm decrement-btn" data-id="${item.producto_id}" data-index="${index}">-</button>
                </td>
            `;

            cartItemsContainer.appendChild(row);
            totalCarrito += item.cantidad * item.precio;
        });

        totalPriceElement.textContent = `$${totalCarrito.toFixed(2)}`;
        calcularVuelto();

        // Reasignar eventos a botones dinámicos
        document.querySelectorAll(".increment-btn").forEach(button => {
            button.addEventListener("click", (e) => {
                const productoId = parseInt(e.target.dataset.id);
                incrementarCantidad(productoId);
            });
        });

        document.querySelectorAll(".decrement-btn").forEach(button => {
            button.addEventListener("click", (e) => {
                const productoId = parseInt(e.target.dataset.id);
                eliminarDelCarrito(productoId);
            });
        });
    }

    function incrementarCantidad(productoId) {
        const productoExistente = carrito.find(item => item.producto_id === productoId);
        if (productoExistente) {
            productoExistente.cantidad += 1;
            actualizarCarrito();
        }
    }

    function eliminarDelCarrito(productoId) {
        const productoIndex = carrito.findIndex(item => item.producto_id === productoId);
        if (productoIndex !== -1) {
            carrito[productoIndex].cantidad -= 1;
            if (carrito[productoIndex].cantidad <= 0) {
                carrito.splice(productoIndex, 1); // Elimina el producto si la cantidad llega a 0
            }
            actualizarCarrito();
        }
    }

    // Confirmar compra
    confirmarCompraButton.addEventListener("click", async () => {
        if (carrito.length === 0) {
            alert("El carrito está vacío.");
            return;
        }

        const tipoVenta = document.querySelector(".btn-group[aria-label='Tipo de Venta'] .active")?.id || "boleta";
        const formaPago = document.querySelector(".btn-group[aria-label='Forma de Pago'] .active")?.id || "efectivo";
        const clientePaga = parseFloat(document.getElementById("cantidad_pagada").value) || 0;

        try {
            const response = await fetch("/cashier/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify({
                    carrito,
                    tipo_venta: tipoVenta,
                    forma_pago: formaPago,
                    cliente_paga: clientePaga
                })
            });

            const data = await response.json();

            if (response.ok) {
                alert("Compra confirmada con éxito.");
                window.open(data.reporte_url, "_blank");
                carrito = [];
                actualizarCarrito();
            } else {
                alert(`Error al confirmar compra: ${data.error || "Ocurrió un error inesperado"}`);
            }
        } catch (error) {
            console.error("Error al confirmar compra:", error);
            alert("Error al confirmar compra.");
        }
    });

    function getCSRFToken() {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split("=");
            if (name === "csrftoken") return value;
        }
        return null;
    }
});
