from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Importowanie blueprintów i modeli po zainicjalizowaniu aplikacji
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .models import User, GameLog  # Import po zainicjalizowaniu 'db'

    return app
