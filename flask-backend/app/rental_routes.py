from flask import Blueprint, request, jsonify
from app import db
from app.models import Rental, Inventory, Customer, Staff, Film
from datetime import datetime

rental_bp = Blueprint("rental", __name__)

@rental_bp.route("/rent", methods=["POST"])
def rent_movie():
    data = request.json
    film_id = data.get("film_id")
    store_id = data.get("store_id")
    customer_id = data.get("customer_id")
    staff_id = data.get("staff_id")
    force_register = data.get("force_register", False)

    if not film_id or not store_id or not customer_id or not staff_id:
        return jsonify({"error": "Todos los campos son obligatorios"}), 400

    # Buscar la primera copia disponible de la película en la tienda
    inventory = Inventory.query.filter_by(film_id=film_id, store_id=store_id).outerjoin(
        Rental, (Rental.inventory_id == Inventory.inventory_id) & (Rental.return_date == None)
    ).filter(Rental.rental_id == None).first()

    if not inventory:
        return jsonify({"error": "No hay copias disponibles de esta película en la tienda"}), 404

    staff = Staff.query.get(staff_id)
    customer = Customer.query.get(customer_id)

    if not staff or not customer:
        return jsonify({"error": "Cliente o empleado no válido"}), 404

    # 🚨 Cliente no pertenece a la tienda
    if customer.store_id != store_id:
        if not force_register:
            return jsonify({
                "error": "El cliente no pertenece a esta tienda.",
                "require_confirmation": True
            }), 409

        # Verificar si ya existe ese cliente en la tienda (por correo)
        existing = Customer.query.filter_by(email=customer.email, store_id=store_id).first()
        if existing:
            customer = existing
        else:
            # Crear nuevo cliente para esta tienda
            new_customer = Customer(
                first_name=customer.first_name,
                last_name=customer.last_name,
                email=customer.email,
                address_id=customer.address_id,
                store_id=store_id,
                active=1
            )
            db.session.add(new_customer)
            db.session.commit()
            customer = new_customer

    # Verificar staff
    if staff.store_id != store_id:
        return jsonify({"error": "El empleado no pertenece a la tienda seleccionada"}), 400

    # Ya tiene esta película rentada sin devolver
    existing_rental = Rental.query.filter_by(
        inventory_id=inventory.inventory_id,
        customer_id=customer.customer_id,
        return_date=None
    ).first()

    if existing_rental:
        return jsonify({"error": "No puedes rentar esta película hasta devolver la anterior"}), 400

    # Registrar alquiler
    rental = Rental(
        inventory_id=inventory.inventory_id,
        customer_id=customer.customer_id,
        staff_id=staff_id,
        rental_date=datetime.utcnow(),
    )

    db.session.add(rental)
    db.session.commit()

    return jsonify({
        "message": "Película rentada con éxito",
        "rental_id": rental.rental_id
    })

@rental_bp.route("/return/<int:rental_id>", methods=["PUT"])
def return_movie(rental_id):
    rental = Rental.query.get(rental_id)
    if not rental:
        return jsonify({"error": "Alquiler no encontrado"}), 404

    rental.return_date = datetime.utcnow()
    db.session.commit()
    return jsonify({"message": "Película devuelta correctamente"})


@rental_bp.route("/rentals/customer/", methods=["GET"])
def get_rentals():
    customer_id = request.args.get("customer_id")
    rental_type = request.args.get("type")
    store_id = request.args.get("store_id")

    if not customer_id or not store_id:
        return jsonify({"error": "customer_id y store_id son requeridos"}), 400

    query = (
        db.session.query(
            Rental.rental_id,
            Rental.rental_date,
            Rental.return_date,
            Film.title.label("film_title"),
            Staff.first_name,
            Staff.last_name
        )
        .select_from(Rental)
        .join(Inventory, Rental.inventory_id == Inventory.inventory_id)
        .join(Film, Inventory.film_id == Film.film_id)
        .join(Staff, Rental.staff_id == Staff.staff_id)
        .filter(Rental.customer_id == customer_id)
        .filter(Inventory.store_id == store_id)  # <- Aquí se asegura que sea de esa tienda
    )

    if rental_type == "recent":
        query = query.order_by(Rental.rental_date.desc()).limit(5)

    rentals = query.all()

    result = []
    for r in rentals:
        result.append({
            "rental_id": r.rental_id,
            "rental_date": r.rental_date,
            "return_date": r.return_date,
            "film_title": r.film_title,
            "staff_name": f"{r.first_name} {r.last_name}",
            "status": "Devuelta" if r.return_date else "Pendiente"
        })

    return jsonify(result)

@rental_bp.route("/associate_customer", methods=["POST"])
def associate_customer():
    data = request.json
    customer_id = data.get("customer_id")
    target_store_id = data.get("store_id")

    original = Customer.query.get(customer_id)
    if not original:
        return jsonify({"error": "Cliente no encontrado"}), 404

    # Clonar cliente pero con diferente store
    new_customer = Customer(
        store_id=target_store_id,
        first_name=original.first_name,
        last_name=original.last_name,
        email=original.email,
        address_id=original.address_id,
        active=original.active,
        create_date=datetime.utcnow()
    )

    db.session.add(new_customer)
    db.session.commit()

    return jsonify({"message": "Cliente asociado a la tienda con éxito", "new_customer_id": new_customer.customer_id})
