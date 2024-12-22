document.addEventListener("DOMContentLoaded", () => {
    const cerrarCajaBtn = document.getElementById("cerrar-caja-btn");
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
                button.classList.add("active");
                localStorage.setItem(storageKey, selectedButtonId);
            } else {
                button.classList.remove("active");
            }
        });
    }

    // Mostrar notificaciones con alertas simples (en vez de Toasts o Modales)
    function showAlert(message, type = "success") {
        const prefix = type === "success" ? "[Éxito]" : "[Error]";
        alert(`${prefix} ${message}`);
    }

    // Obtener el token CSRF
    function getCSRFToken() {
        const cookies = document.cookie.split("; ");
        for (let cookie of cookies) {
            const [name, value] = cookie.split("=");
            if (name === "csrftoken") return value;
        }
        return null;
    }

    // Calcular el vuelto
    function calcularVuelto() {
        const cantidadPagada = parseFloat(cantidadPagadaInput.value) || 0;
        const totalCarrito = parseFloat(totalPriceElement.textContent.replace("$", "")) || 0;

        const vuelto = cantidadPagada - totalCarrito;
        vueltoElement.textContent = `$${vuelto.toFixed(2)}`;
    }

    if (cantidadPagadaInput) {
        cantidadPagadaInput.addEventListener("input", calcularVuelto);
    }

    // Configuración de botones para Tipo de Venta
    document.getElementById("boleta").addEventListener("click", () => toggleButtonGroup('.btn-group[aria-label="Tipo de Venta"] .btn', "boleta", "tipo_venta"));
    document.getElementById("factura").addEventListener("click", () => toggleButtonGroup('.btn-group[aria-label="Tipo de Venta"] .btn', "factura", "tipo_venta"));

    // Configuración de botones para Forma de Pago
    document.getElementById("efectivo").addEventListener("click", () => toggleFormaPago("efectivo"));
    document.getElementById("debito").addEventListener("click", () => toggleFormaPago("debito"));
    document.getElementById("credito").addEventListener("click", () => toggleFormaPago("credito"));

    function toggleFormaPago(metodo) {
        toggleButtonGroup('.btn-group[aria-label="Forma de Pago"] .btn', metodo, "forma_pago");
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
        if (!query) {
            showAlert("Por favor, ingresa un término de búsqueda.", "error");
            return;
        }

        try {
            const response = await fetch(`/cashier/buscar-producto/?q=${query}`);
            if (!response.ok) throw new Error("Error al buscar productos.");
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
            showAlert("Error al buscar productos.", "error");
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
    }

    // Manejo de botones dinámicos en carrito
    cartItemsContainer.addEventListener("click", (e) => {
        if (e.target.classList.contains("increment-btn")) {
            const productoId = parseInt(e.target.dataset.id);
            incrementarCantidad(productoId);
        } else if (e.target.classList.contains("decrement-btn")) {
            const productoId = parseInt(e.target.dataset.id);
            eliminarDelCarrito(productoId);
        }
    });

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
                carrito.splice(productoIndex, 1);
            }
            actualizarCarrito();
        }
    }

    // Confirmar compra
    confirmarCompraButton.addEventListener("click", async () => {
        if (carrito.length === 0) {
            showAlert("El carrito está vacío.", "error");
            return;
        }

        const tipoVenta = document.querySelector(".btn-group[aria-label='Tipo de Venta'] .active")?.id || "boleta";
        const formaPago = document.querySelector(".btn-group[aria-label='Forma de Pago'] .active")?.id || "efectivo";
        const clientePaga = parseFloat(cantidadPagadaInput.value) || 0;

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
                showAlert("Compra confirmada con éxito.", "success");
                carrito = [];
                actualizarCarrito();
            } else {
                showAlert(data.error || "Error al confirmar compra.", "error");
            }
        } catch (error) {
            console.error("Error al confirmar compra:", error);
            showAlert("Error al confirmar compra.", "error");
        }
    });

    // Cerrar caja
    if (cerrarCajaBtn) {
        cerrarCajaBtn.addEventListener("click", async () => {
            console.log("evento detectado");
            try {
                const response = await fetch("/cashier/cerrar_caja/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCSRFToken(),
                        "Content-Type": "application/json"
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        showAlert(data.mensaje || "Caja cerrada con éxito.", "success");
                        window.location.href = "/cashier/";
                    } else {
                        showAlert(data.error || "Error al cerrar la caja.", "error");
                    }
                } else {
                    showAlert("Error al cerrar la caja. Verifica los permisos.", "error");
                }
            } catch (error) {
                console.error("Error al cerrar caja:", error);
                showAlert("Ocurrió un error al cerrar la caja.", "error");
            }
        });
    }
});
