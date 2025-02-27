from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO

db = SQLAlchemy()
DB_NAME = "database.db"
bcrypt = Bcrypt()
migrate = Migrate()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "s"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    db.init_app(app)
    migrate = Migrate(app, db)
    socketio.init_app(app)

    from .views import views
    from .auth import auth
    from .sockets import sockets

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(sockets, url_prefix='/')

    from .models import User, GameLog

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('app/' + DB_NAME):
        db.create_all(app=app)
        print("Database created")