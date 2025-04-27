document.addEventListener("DOMContentLoaded", () => {
    const cerrarCajaBtn = document.getElementById("close-cash-button");
    const confirmarCompraButton = document.getElementById("confirmar-compra");
    const cantidadPagadaInput = document.getElementById("cantidad_pagada");
    const vueltoElement = document.getElementById("vuelto");
    const totalPriceElement = document.getElementById("total-price");
    const cartItemsContainer = document.getElementById("cart-items");
    const searchButton = document.getElementById("product-search-button");
    const searchInput = document.getElementById("product-search-input");
    const resultsList = document.getElementById("product-search-results");
    const formaPagoButtons = document.querySelectorAll(".btn-group button");
    let carrito = new Map();
    let totalCarrito = 0;

    function getCSRFToken() {
        return document.cookie.split("; ").find(row => row.startsWith("csrftoken="))?.split("=")[1] || null;
    }

    function showToast(message, type = "success") {
        let toastContainer = document.getElementById("toast-container");
        if (!toastContainer) {
            toastContainer = document.createElement("div");
            toastContainer.id = "toast-container";
            toastContainer.style.position = "fixed";
            toastContainer.style.top = "20px";
            toastContainer.style.right = "20px";
            toastContainer.style.zIndex = "1050";
            document.body.appendChild(toastContainer);
        }

        const toastId = `toast-${Date.now()}`;
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0 show" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body fs-6">
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        toastContainer.innerHTML += toastHtml;
        const toastElement = document.getElementById(toastId);
        const toastInstance = new bootstrap.Toast(toastElement, { delay: 4000 });
        toastInstance.show();
        setTimeout(() => toastElement.remove(), 4500);
    }

    function calcularVuelto() {
        const cantidadPagada = parseFloat(cantidadPagadaInput.value) || 0;
        const totalCarrito = parseFloat(totalPriceElement.textContent.replace("$", "")) || 0;
        const vuelto = cantidadPagada - totalCarrito;
        vueltoElement.textContent = `$${vuelto.toFixed(2)}`;
    }

    if (cantidadPagadaInput) cantidadPagadaInput.addEventListener("input", calcularVuelto);

    function debounce(func, delay = 300) {
        let timeout;
        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => func(...args), delay);
        };
    }

    searchButton.addEventListener("click", debounce(async () => {
        const query = searchInput.value.trim();
        if (!query) return showToast("Ingresa un término de búsqueda.", "warning");

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
                li.innerHTML = `${producto.nombre} - $${producto.precio_venta} 
                    <button class="btn btn-success btn-sm ml-2" 
                        data-id="${producto.id}" 
                        data-nombre="${producto.nombre}" 
                        data-precio="${producto.precio_venta}">+</button>`;
                resultsList.appendChild(li);
            });
        } catch (error) {
            console.error("Error al buscar productos:", error);
            showToast("Error en la búsqueda.", "danger");
        }
    }, 500));

    resultsList.addEventListener("click", (e) => {
        if (e.target.tagName === "BUTTON") {
            const { id, nombre, precio } = e.target.dataset;
            agregarAlCarrito(parseInt(id), nombre, parseFloat(precio));
        }
    });

    function agregarAlCarrito(productoId, nombre, precio) {
        if (!productoId) {
            console.error("Error: Falta productoId al agregar al carrito");
            return;
        }

        const cantidad = carrito.has(productoId) ? carrito.get(productoId).cantidad + 1 : 1;
        carrito.set(productoId, { producto_id: productoId, nombre, precio, cantidad });

        actualizarCarrito();
    }

    function actualizarCarrito() {
        cartItemsContainer.innerHTML = "";
        totalCarrito = 0;

        carrito.forEach(({ producto_id, nombre, precio, cantidad }) => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${cantidad}</td>
                <td>${nombre}</td>
                <td>$${(cantidad * precio).toFixed(2)}</td>
                <td>
                    <button class="btn btn-success btn-sm" data-id="${producto_id}" data-action="increment">+</button>
                    <button class="btn btn-danger btn-sm" data-id="${producto_id}" data-action="decrement">-</button>
                </td>
            `;
            cartItemsContainer.appendChild(row);
            totalCarrito += cantidad * precio;
        });

        totalPriceElement.textContent = `$${totalCarrito.toFixed(2)}`;
        calcularVuelto();
    }

    cartItemsContainer.addEventListener("click", (e) => {
        const productoId = parseInt(e.target.dataset.id);
        if (!productoId) return;

        if (e.target.dataset.action === "increment") {
            carrito.get(productoId).cantidad++;
        } else if (e.target.dataset.action === "decrement") {
            carrito.get(productoId).cantidad--;
            if (carrito.get(productoId).cantidad <= 0) carrito.delete(productoId);
        }
        actualizarCarrito();
    });

    confirmarCompraButton.addEventListener("click", async () => {
        if (carrito.size === 0) return showToast("El carrito está vacío.", "warning");

        const carritoArray = Array.from(carrito.values());
        console.log("🔍 Enviando carrito:", carritoArray);

        try {
            const response = await fetch("/cashier/", {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-CSRFToken": getCSRFToken() },
                body: JSON.stringify({ carrito: carritoArray })
            });

            if (!response.ok) {
                const data = await response.json();
                return showToast(data.error || "Error en la compra.", "danger");
            }

            showToast("Compra confirmada con éxito.", "success");
            carrito.clear();
            actualizarCarrito();
        } catch (error) {
            console.error("Error al confirmar compra:", error);
            showToast("Error al procesar la compra.", "danger");
        }
    });


        // Llenar automáticamente el monto al seleccionar débito o crédito
        formaPagoButtons.forEach(button => {
            button.addEventListener("click", () => {
                if (button.id === "debito" || button.id === "credito") {
                    cantidadPagadaInput.value = totalCarrito.toFixed(2);
                    calcularVuelto();
                }
            });
        }); 
    

        if (cerrarCajaBtn) {
            cerrarCajaBtn.addEventListener("click", async () => {
                try {
                    const response = await fetch("/cashier/cerrar_caja/", {
                        method: "POST",
                        headers: {
                            "X-CSRFToken": getCSRFToken(),
                            "Content-Type": "application/json"
                        }
                    });
        
                    const data = await response.json();
                    console.log("📊 Respuesta del servidor al cerrar caja:", data);  // Debugging
        
                    if (data.success) {
                        showToast(`Caja cerrada con éxito.`, "success");
        
                        // 🔀 Redirigir solo si el ID de la caja está presente
                        if (data.caja_id) {
                            console.log(`🔀 Redirigiendo a: /cashier/detalle-caja/${data.caja_id}/`);
                            window.location.href = `/cashier/detalle-caja/${data.caja_id}/`;
                        } else {
                            console.error("⚠️ Error: 'caja_id' no está presente en la respuesta.");
                            showToast("Error: No se pudo obtener el ID de la caja.", "danger");
                        }
                    } else {
                        showToast(data.error || "Error al cerrar la caja.", "danger");
                    }
                } catch (error) {
                    console.error("❌ Error al cerrar caja:", error);
                    showToast("Error al cerrar la caja.", "danger");
                }
            });
        }
        
        
});
