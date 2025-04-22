let selectedStoreId = null;
let selectedStaffId = null;

document.addEventListener("DOMContentLoaded", async () => {
    await loadStoresAndStaff();
    if (selectedStoreId) {
        getMovies(selectedStoreId);
    }
});

async function loadStoresAndStaff() {
    try {
        const storeRes = await fetch("store/stores");
        const stores = await storeRes.json();

        const storeSelect = document.getElementById("storeSelect");
        const staffSelect = document.getElementById("staffSelect");

        // Llenar el select de tiendas
        storeSelect.innerHTML = stores.map(store =>
            `<option value="${store.store_id}">Tienda ${store.store_id}</option>`
        ).join("");

        // Obtener el primer store_id como seleccionado inicialmente
        selectedStoreId = storeSelect.value;

        // Cargar el staff para la tienda seleccionada
        await loadStaffByStore(selectedStoreId);

        // Escuchar cambios de tienda
        storeSelect.addEventListener("change", async (e) => {
            selectedStoreId = e.target.value;
            await loadStaffByStore(selectedStoreId); // cargar staff correspondiente
            getMovies(selectedStoreId); // cargar películas
        });

        // Escuchar cambios de empleado
        staffSelect.addEventListener("change", (e) => {
            selectedStaffId = e.target.value;
        });

        // Guardar empleado inicialmente seleccionado
        selectedStaffId = staffSelect.value;

    }
    catch (error) {
        console.error("Error al cargar tiendas o empleados:", error);
        Swal.fire("Error", "No se pudieron cargar las tiendas o empleados.", "error");
    }
}

async function loadStaffByStore(storeId) {
    try {
        const res = await fetch(`staff/staff?store_id=${storeId}`);
        const staff = await res.json();

        const staffSelect = document.getElementById("staffSelect");

        if (staff.length === 0) {
            staffSelect.innerHTML = `<option disabled selected>No hay empleados disponibles</option>`;
            selectedStaffId = null;
        }
        else {
            staffSelect.innerHTML = staff.map(s =>
                `<option value="${s.staff_id}">${s.first_name} ${s.last_name}</option>`
            ).join("");
            selectedStaffId = staff[0].staff_id;
        }
    }
    catch (error) {
        console.error("Error al cargar empleados:", error);
        Swal.fire("Error", "No se pudo cargar el personal para la tienda seleccionada.", "error");
    }
}


async function getMovies(storeId) {
    try {
        const response = await fetch(`/films/store/${storeId}`);
        if (!response.ok) throw new Error("Error en la respuesta del servidor");

        const movies = await response.json();
        displayMovies(movies);
    }
    catch (error) {
        console.error("Error al obtener películas:", error);
        Swal.fire("Error", "No se pudieron cargar las películas.", "error");
    }
}

function displayMovies(movies) {
    const table = document.getElementById("movieList");
    table.innerHTML = "";

    movies.forEach((movie) => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${movie.title}</td>
            <td>${movie.release_year}</td>
            <td>${movie.rental_duration} días</td>
            <td>${movie.rental_rate.toFixed(2)}</td>
            <td>${movie.rating}</td>
            <td>${movie.num_copies}</td> <!-- Nueva celda -->
            <td><button class="rent-btn" onclick="rentMovie(${movie.id},${selectedStoreId})">Rentar</button></td>
        `;

        table.appendChild(row);
    });
}

async function rentMovie(film_id, store_id) {
    const staff_id = selectedStaffId;

    if (!staff_id) {
        Swal.fire("Error", "Debes seleccionar un empleado", "error");
        return;
    }

    const { value: customer_id } = await Swal.fire({
        title: "ID del cliente",
        input: "number",
        inputLabel: "Por favor ingresa el ID del cliente",
        inputPlaceholder: "Ej: 1",
        confirmButtonText: "Continuar",
        showCancelButton: true,
        inputValidator: (value) => {
            if (!value) return "El ID del cliente es obligatorio";
        },
    });

    if (!customer_id) {
        Swal.fire("Cancelado", "No se rentó la película", "info");
        return;
    }

    const tryRent = async (cust_id) => {
        const res = await fetch("rental/rent", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                film_id,
                store_id,
                customer_id: cust_id,
                staff_id
            })
        });

        const data = await res.json();

        if (res.ok) {
            Swal.fire("Éxito", "Película rentada con éxito", "success");
        } else if (res.status === 409 && data.error.includes("no pertenece a esta tienda")) {
            const confirm = await Swal.fire({
                title: "Cliente no asociado a esta tienda",
                text: "¿Deseas asociar este cliente a la tienda seleccionada?",
                icon: "warning",
                showCancelButton: true,
                confirmButtonText: "Sí, asociar",
                cancelButtonText: "No"
            });

            if (confirm.isConfirmed) {
                const assocRes = await fetch("rental/associate_customer", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        customer_id: cust_id,
                        store_id
                    })
                });

                const assocData = await assocRes.json();

                if (assocRes.ok) {
                    await tryRent(assocData.new_customer_id);
                } else {
                    Swal.fire("Error", assocData.error || "No se pudo asociar el cliente", "error");
                }
            }
        } else {
            Swal.fire("Error", data.error || "Error en la renta", "error");
        }
    };

    await tryRent(customer_id);
}




async function getRentals(type) {
    try {
        const { value: customerId } = await Swal.fire({
            title: "Ingrese el ID del cliente",
            input: "number",
            inputLabel: "Customer ID",
            inputPlaceholder: "Ejemplo: 1",
            showCancelButton: true
        });

        if (!customerId) return;

        if (!selectedStoreId) {
            Swal.fire("Error", "Debe seleccionar una tienda antes.", "error");
            return;
        }

        const response = await fetch(
            `rental/rentals/customer/?customer_id=${customerId}&store_id=${selectedStoreId}&type=${type}`
        );

        if (!response.ok) {
            throw new Error("Error en la respuesta del servidor");
        }

        const rentals = await response.json();

        const table = document.getElementById("rentalList");
        table.innerHTML = "";

        rentals.forEach(rental => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${rental.rental_id}</td>
                <td>${rental.staff_name}</td>
                <td>${rental.film_title}</td>
                <td>${new Date(rental.rental_date).toLocaleString()}</td>
                <td>${rental.status}</td>
                <td>
                    ${rental.status === "Pendiente"
                        ? `<button onclick="returnMovie(${rental.rental_id})">Devolver</button>`
                        : `<span>✓</span>`
                    }
                </td>
            `;
            table.appendChild(row);
        });

        document.getElementById("rentals").style.display = "block";

    }
    catch (error) {
        console.error("Error al obtener rentas:", error);
        Swal.fire("Error", error.message, "error");
    }
}


function showSection(sectionId) {
        const sections = ["home", "movies", "rentals"];
        sections.forEach(id => {
            const section = document.getElementById(id);
            if (section) section.style.display = (id === sectionId) ? "block" : "none";
        });
    }
    
async function returnMovie(rental_id) {
    const confirm = await Swal.fire({
        title: "¿Devolver película?",
        text: `¿Estás seguro de devolver el alquiler #${rental_id}?`,
        icon: "warning",
        showCancelButton: true,
        confirmButtonText: "Sí, devolver",
        cancelButtonText: "Cancelar"
    });

    if (!confirm.isConfirmed) return;

    const res = await fetch(`/rental/return/${rental_id}`, {
        method: "PUT"
    });

    const data = await res.json();

    if (res.ok) {
        Swal.fire("Éxito", data.message, "success");
        loadRentals(); // 👈 Recarga la lista de alquileres
    } else {
        Swal.fire("Error", data.error || "No se pudo devolver la película", "error");
    }
}
