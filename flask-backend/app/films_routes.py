from flask import Blueprint, jsonify, request
from .models import Film, Inventory, Store, Rental
from . import db
from sqlalchemy import func
from sqlalchemy.orm import aliased



main = Blueprint("films", __name__)

@main.route("store/<int:store_id>", methods=["GET"])
def get_films(store_id):
    # Alias para rental
    rental_alias = aliased(Rental)

    films = (
        db.session.query(
            Film.film_id,
            Film.title,
            Film.release_year,
            Film.rental_duration,
            Film.rental_rate,
            Film.length,
            Film.rating,
            func.count(Inventory.inventory_id).label("num_copies")
        )
        .join(Inventory)
        .outerjoin(
            rental_alias,
            (Inventory.inventory_id == rental_alias.inventory_id)
            & (rental_alias.return_date == None)
        )
        .filter(Inventory.store_id == store_id)
        .filter(rental_alias.rental_id == None)  # Solo copias no alquiladas
        .group_by(Film.film_id)
        .all()
    )

    films_list = [
        {
            "id": film.film_id,
            "title": film.title,
            "release_year": film.release_year,
            "rental_duration": film.rental_duration,
            "rental_rate": film.rental_rate,
            "length": film.length,
            "rating": film.rating,
            "num_copies": film.num_copies
        }
        for film in films
    ]

    return jsonify(films_list)

@main.route("/film/<int:film_id>", methods=["GET"])
def get_film(film_id):
    film = Film.query.get_or_404(film_id)
    return jsonify(film.to_dict())
