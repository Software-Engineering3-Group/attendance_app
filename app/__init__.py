import os
from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

load_dotenv()  # load variables from .env

def create_app():
    # Paths for templates and static files relative to this file (__init__.py)
    template_path = os.path.join(os.path.dirname(__file__), "templates")
    static_path = os.path.join(os.path.dirname(__file__), "static")

    # Create Flask app
    app = Flask(__name__, template_folder=template_path, static_folder=static_path)

    # Config
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///dev.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    # Lazy imports
    from .models import db
    db.init_app(app)

    # Database migration
    migrate = Migrate(app, db)

    # Login manager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    # JWT manager
    jwt = JWTManager(app)

    # Blueprints
    from .auth import auth_bp
    from .main import main_bp
    from .courses import courses_bp
    from .attendance import attendance_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)
    app.register_blueprint(courses_bp, url_prefix="/courses")
    app.register_blueprint(attendance_bp, url_prefix="/attendance")

    # User loader
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
