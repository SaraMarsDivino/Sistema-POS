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

    const tipoVentaInput = { value: "boleta" };
    const formaPagoInput = document.getElementById("forma_pago");

    const tipoVentaButtons = [document.getElementById("boleta"), document.getElementById("factura")];
    const formaPagoButtons = [document.getElementById("efectivo"), document.getElementById("debito"), document.getElementById("credito")];

    let carrito = new Map();
    let totalCarrito = 0;

    function getCSRFToken() {
        return document.cookie.split("; ").find(row => row.startsWith("csrftoken="))?.split("=")[1] || null;
    }

    function showToast(message, type = "success") {
        const toastContainer = document.getElementById("toast-container") || (() => {
            const tc = document.createElement("div");
            tc.id = "toast-container";
            tc.style.position = "fixed";
            tc.style.top = "20px";
            tc.style.right = "20px";
            tc.style.zIndex = "1050";
            document.body.appendChild(tc);
            return tc;
        })();

        const toastId = `toast-${Date.now()}`;
        toastContainer.innerHTML += `
            <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0 show" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body fs-6">${message}</div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;
        const toastElement = document.getElementById(toastId);
        new bootstrap.Toast(toastElement, { delay: 4000 }).show();
        setTimeout(() => toastElement.remove(), 4500);
    }

    function calcularVuelto() {
        const pagado = parseFloat(cantidadPagadaInput.value) || 0;
        const total = parseFloat(totalPriceElement.textContent.replace("$", "")) || 0;
        const vuelto = pagado - total;
        vueltoElement.textContent = `$${vuelto.toFixed(2)}`;
    }

    cantidadPagadaInput.addEventListener("input", calcularVuelto);

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
            const res = await fetch(`/cashier/buscar-producto/?q=${query}`);
            const data = await res.json();
            resultsList.innerHTML = "";

            if (data.productos.length === 0) {
                resultsList.innerHTML = "<li>No se encontraron productos.</li>";
                return;
            }

            data.productos.forEach(p => {
                const li = document.createElement("li");
                li.innerHTML = `${p.nombre} - $${p.precio_venta} 
                    <button class="btn btn-success btn-sm ml-2" 
                        data-id="${p.id}" data-nombre="${p.nombre}" data-precio="${p.precio_venta}">+</button>`;
                resultsList.appendChild(li);
            });
        } catch {
            showToast("Error en la búsqueda.", "danger");
        }
    }));

    resultsList.addEventListener("click", (e) => {
        if (e.target.tagName === "BUTTON") {
            const { id, nombre, precio } = e.target.dataset;
            agregarAlCarrito(parseInt(id), nombre, parseFloat(precio));
        }
    });

    function agregarAlCarrito(productoId, nombre, precio) {
        if (!productoId) return;
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

        const item = carrito.get(productoId);
        if (e.target.dataset.action === "increment") item.cantidad++;
        if (e.target.dataset.action === "decrement") {
            item.cantidad--;
            if (item.cantidad <= 0) carrito.delete(productoId);
        }

        actualizarCarrito();
    });

    tipoVentaButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            tipoVentaButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            tipoVentaInput.value = btn.id;
        });
    });

    formaPagoButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            formaPagoButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            formaPagoInput.value = btn.id;

            if (btn.id === "debito" || btn.id === "credito") {
                cantidadPagadaInput.value = totalCarrito.toFixed(2);
            } else {
                cantidadPagadaInput.value = "";
            }

            calcularVuelto();
        });
    });

    confirmarCompraButton.addEventListener("click", async () => {
        if (!formaPagoInput.value) return showToast("Selecciona un método de pago", "danger");
        if (carrito.size === 0) return showToast("El carrito está vacío", "warning");

        const confirmar = confirm("¿Deseas imprimir el comprobante?");
        if (!confirmar) return;

        try {
            const res = await fetch("/cashier/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken()
                },
                body: JSON.stringify({
                    carrito: Array.from(carrito.values()),
                    tipo_venta: tipoVentaInput.value,
                    forma_pago: formaPagoInput.value,
                    cliente_paga: parseFloat(cantidadPagadaInput.value) || 0
                })
            });

            const data = await res.json();
            if (!res.ok || !data.success) return showToast(data.error || "Error al confirmar", "danger");

            showToast("Compra confirmada con éxito", "success");
            carrito.clear();
            actualizarCarrito();

            if (data.reporte_url) window.open(data.reporte_url, "_blank");
        } catch (err) {
            console.error("Error al confirmar compra:", err);
            showToast("Error al procesar la compra", "danger");
        }
    });

    if (cerrarCajaBtn) {
        cerrarCajaBtn.addEventListener("click", async () => {
            try {
                const res = await fetch("/cashier/cerrar_caja/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCSRFToken(),
                        "Content-Type": "application/json"
                    }
                });
                const data = await res.json();
                if (data.success && data.caja_id) {
                    showToast("Caja cerrada con éxito.", "success");
                    window.location.href = `/cashier/detalle-caja/${data.caja_id}/`;
                } else {
                    showToast(data.error || "Error al cerrar la caja.", "danger");
                }
            } catch (err) {
                showToast("Error al cerrar la caja", "danger");
            }
        });
    }
});
