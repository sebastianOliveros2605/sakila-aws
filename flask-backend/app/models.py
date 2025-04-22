from app import db
from datetime import datetime
from sqlalchemy.orm import relationship


class Customer(db.Model):
    __tablename__ = "customer"

    customer_id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey("store.store_id"), nullable=False)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    email = db.Column(db.String(50))
    address_id = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, default=True)
    create_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_update = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    rentals = db.relationship("Rental", backref="customer")


class Staff(db.Model):
    __tablename__ = "staff"

    staff_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    address_id = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(50))
    store_id = db.Column(db.Integer, nullable=False)
    active = db.Column(db.Boolean, default=True)
    username = db.Column(db.String(16), nullable=False)
    password = db.Column(db.String(40))
    last_update = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Film(db.Model):
    __tablename__ = "film"

    film_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    release_year = db.Column(db.Integer)
    rental_duration = db.Column(db.Integer)
    rental_rate = db.Column(db.Float)
    length = db.Column(db.Integer)
    replacement_cost = db.Column(db.Float)
    rating = db.Column(db.String(10))
    last_update = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    inventory = db.relationship("Inventory", backref="film")



class Inventory(db.Model):
    __tablename__ = "inventory"

    inventory_id = db.Column(db.Integer, primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey("film.film_id"), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('store.store_id'), nullable=False)
    last_update = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    rentals = db.relationship("Rental", backref="inventory")


class Rental(db.Model):
    __tablename__ = "rental"

    rental_id = db.Column(db.Integer, primary_key=True)
    rental_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey("inventory.inventory_id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customer.customer_id"), nullable=False)
    return_date = db.Column(db.DateTime, nullable=True)
    staff_id = db.Column(db.Integer, db.ForeignKey("staff.staff_id"), nullable=False)
    last_update = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Store(db.Model):
    __tablename__ = 'store'

    store_id = db.Column(db.Integer, primary_key=True)
    manager_staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'), nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)

    # Relaciones
    manager = relationship('Staff', backref='manages_store', foreign_keys=[manager_staff_id])
    address = relationship('Address', backref='stores')
    inventory = relationship('Inventory', backref='store', lazy=True)
    customers = relationship('Customer', backref='store', lazy=True)

class Address(db.Model):
    __tablename__ = 'address'
    address_id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(50))