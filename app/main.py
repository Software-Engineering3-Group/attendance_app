from flask import Blueprint, render_template
from flask_login import login_required, current_user

main_bp = Blueprint(
    'main_bp', 
    __name__, 
    template_folder='app/templates'
)

@main_bp.route("/")
def landing():
    return render_template("landing.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")
