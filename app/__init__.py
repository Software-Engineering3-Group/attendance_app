import os
from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()  # Load environment variables from .env

def create_app():
    # Paths for templates and static files
    template_path = os.path.join(os.path.dirname(__file__), "templates")
    static_path = os.path.join(os.path.dirname(__file__), "static")

    # Create Flask app
    app = Flask(__name__, template_folder=template_path, static_folder=static_path)

    # Configuration
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev_secret_key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:password@localhost/attendance_db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "jwt_secret_key")

    # Initialize database
    from .models import db
    db.init_app(app)

    # Initialize migrations
    Migrate(app, db)
    
    # Login manager setup
    login_manager = LoginManager()
    login_manager.login_view = "auth_bp.login"
    login_manager.init_app(app)

    # JWT setup
    JWTManager(app)

    # Import and register blueprints
    from .auth import auth_bp
    from .main import main_bp
    from .courses import courses_bp
    from .attendance import attendance_bp
    from .api_routes import api_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)
    app.register_blueprint(courses_bp, url_prefix="/courses")
    app.register_blueprint(attendance_bp, url_prefix="/attendance")
    app.register_blueprint(api_bp)

    # User loader (Flask-Login)
    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ✅ Test database connection immediately (works in scripts like seed.py)
    try:
        with app.app_context():
            db.session.execute(text("SELECT 1"))
            print("✅ Database connected successfully")
    except Exception as e:
        print("❌ Database connection error:", e)

    return app
