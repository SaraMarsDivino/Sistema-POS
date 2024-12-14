document.addEventListener("DOMContentLoaded", () => {
    const barcodeInput = document.getElementById("barcode-input");
    const cartItemsContainer = document.getElementById("cart-items");
    const resultsList = document.getElementById("product-search-results");
    const searchInput = document.getElementById("product-search-input");
    const searchButton = document.getElementById("product-search-button");
    const totalPriceElement = document.getElementById("total-price");
    let carrito = [];
    let totalCarrito = 0;

    // Buscar productos al presionar el botón de búsqueda
    searchButton.addEventListener("click", buscarProductos);

    // Agregar producto al carrito usando código de barras
    barcodeInput.addEventListener("keypress", async (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            const barcode = barcodeInput.value.trim();
            if (!barcode) return;

            try {
                const response = await fetch(`/cashier/buscar-producto/?q=${barcode}`);
                const data = await response.json();

                if (data.productos.length > 0) {
                    const producto = data.productos[0];
                    agregarAlCarrito(producto.id, producto.nombre, parseFloat(producto.precio_venta));
                } else {
                    alert("Producto no encontrado.");
                }
            } catch (error) {
                console.error("Error al buscar producto:", error);
                alert("Error al buscar producto.");
            } finally {
                barcodeInput.value = ""; // Vaciar el campo después de buscar
            }
        }
    });

    // Buscar productos por nombre o código
    async function buscarProductos() {
        const query = searchInput.value.trim();
        if (!query) return;

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
                addButton.textContent = "Agregar";
                addButton.classList.add("btn", "btn-primary", "btn-sm", "ml-2");
                addButton.addEventListener("click", () => agregarAlCarrito(producto.id, producto.nombre, parseFloat(producto.precio_venta)));
                li.appendChild(addButton);
                resultsList.appendChild(li);
            });
        } catch (error) {
            console.error("Error al buscar productos:", error);
            alert("Error al buscar productos.");
        }
    }

    // Agregar productos al carrito
    function agregarAlCarrito(productoId, nombre, precio) {
        const productoExistente = carrito.find(item => item.producto_id === productoId);
        if (productoExistente) {
            productoExistente.cantidad++;
        } else {
            carrito.push({ producto_id: productoId, nombre, precio, cantidad: 1 });
        }
        actualizarCarrito();
    }

    // Actualizar carrito
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
                    <button class="btn btn-success btn-sm increment-btn">+</button>
                    <button class="btn btn-danger btn-sm decrement-btn">-</button>
                </td>
            `;
            cartItemsContainer.appendChild(row);

            totalCarrito += item.cantidad * item.precio;

            row.querySelector(".increment-btn").addEventListener("click", () => {
                item.cantidad++;
                actualizarCarrito();
            });

            row.querySelector(".decrement-btn").addEventListener("click", () => {
                item.cantidad--;
                if (item.cantidad <= 0) carrito.splice(index, 1);
                actualizarCarrito();
            });
        });

        totalPriceElement.textContent = `$${totalCarrito.toFixed(2)}`;
    }
});
