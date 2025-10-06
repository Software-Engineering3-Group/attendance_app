from werkzeug.security import generate_password_hash
from . import db
from .models import User
from . import create_app

def seed_admin():
    app = create_app()  # create Flask app
    with app.app_context():  # activate app context
        # Check if admin exists
        admin = User.query.filter_by(role="admin").first()
        if admin:
            print("Admin already exists")
            return

        # Create admin user
        admin_user = User(
            full_name="System Admin",
            email="admin@dut.ac.za",
            password_hash=generate_password_hash("admin123"),
            role="admin"
        )
        db.session.add(admin_user)
        db.session.commit()
        print("✅ Admin user created successfully")

if __name__ == "__main__":
    seed_admin()
