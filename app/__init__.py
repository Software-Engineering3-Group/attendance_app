import os
from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from sqlalchemy import text

# Load environment variables from .env
load_dotenv()

# Import db and models here
from .models import db, User

def create_app():
    # Paths for templates and static files
    base_dir = os.path.dirname(__file__)
    template_path = os.path.join(base_dir, "templates")
    static_path = os.path.join(base_dir, "static")

    # Create Flask app
    app = Flask(__name__, template_folder=template_path, static_folder=static_path)

    # ---------------- CONFIGURATION ---------------- #
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev_secret_key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:Oct20ber2002@localhost/attendance_db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "jwt_secret_key")

    # ---------------- DATABASE SETUP ---------------- #
    db.init_app(app)
    Migrate(app, db)

    # ---------------- LOGIN MANAGER ---------------- #
    login_manager = LoginManager()
    login_manager.login_view = "auth_bp.login"
    login_manager.init_app(app)

    # ---------------- JWT MANAGER ---------------- #
    JWTManager(app)

    # ---------------- BLUEPRINTS ---------------- #
    from .auth import auth_bp
    from .main import main_bp
    from .courses import courses_bp
    from .attendance import attendance_bp
    from .api_routes import api_bp
    from .admin_routes import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)
    app.register_blueprint(courses_bp, url_prefix="/courses")
    app.register_blueprint(attendance_bp, url_prefix="/attendance")
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # ---------------- USER LOADER ---------------- #
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ---------------- DB CONNECTION TEST ---------------- #
    try:
        with app.app_context():
            db.session.execute(text("SELECT 1"))
            print("✅ Database connected successfully")
    except Exception as e:
        print("❌ Database connection error:", e)

    return app
