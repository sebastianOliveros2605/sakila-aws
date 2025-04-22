from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Inicializar la base de datos
    db.init_app(app)
    CORS(app) 

    # Registrar las rutas
    from .rental_routes import rental_bp
    from .store_routes import store_bp
    from .staff_routes import staff_bp
    from .films_routes import main  # Asegúrate de importar el Blueprint de films

    app.register_blueprint(rental_bp, url_prefix="/rental")
    app.register_blueprint(store_bp, url_prefix="/store")
    app.register_blueprint(staff_bp, url_prefix="/staff")
    app.register_blueprint(main, url_prefix="/films")  
    

    # Ruta principal para servir la página HTML
    @app.route("/")
    def home():
        return render_template("index.html")  # Asegúrate de tener este archivo en /templates

    return app
