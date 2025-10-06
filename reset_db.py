# reset_db.py
import os
import shutil
from app import create_app, db
from sqlalchemy import text  # ✅ Required for raw SQL

# -----------------------------
# Configuration
# -----------------------------
app = create_app()
migrations_dir = os.path.join(os.path.dirname(__file__), "migrations")

with app.app_context():
    # -----------------------------
    # Disable foreign key checks
    # -----------------------------
    print("⚠️ Disabling foreign key checks...")
    db.session.execute(text("SET FOREIGN_KEY_CHECKS=0;"))
    db.session.commit()

    # -----------------------------
    # Drop all tables
    # -----------------------------
    print("⚠️ Dropping all tables...")
    db.drop_all()
    db.session.commit()

    # -----------------------------
    # Re-enable foreign key checks
    # -----------------------------
    print("⚠️ Re-enabling foreign key checks...")
    db.session.execute(text("SET FOREIGN_KEY_CHECKS=1;"))
    db.session.commit()
    print("✅ All tables dropped successfully")

# -----------------------------
# Reset Alembic migrations
# -----------------------------
if os.path.exists(migrations_dir):
    print("⚠️ Removing old migrations...")
    shutil.rmtree(migrations_dir)
    print("✅ Old migrations removed")

print("🐍 Creating new migrations folder and generating initial migration...")
os.system("flask db init")
os.system("flask db migrate -m \"Initial migration after reset\"")
os.system("flask db upgrade")
print("🎉 Database reset and migrations applied successfully!")
