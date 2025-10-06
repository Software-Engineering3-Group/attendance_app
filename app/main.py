from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Faculty, Department, Course, Module, Student, db

main_bp = Blueprint(
    'main_bp', 
    __name__, 
    template_folder='app/templates'
)

# ----------------------
# Landing page
# ----------------------
@main_bp.route("/")
def landing():
    return render_template("landing.html")

# ----------------------
# Lecturer dashboard
# ----------------------
@main_bp.route("/dashboard")
@login_required
def dashboard():
    # Fetch lecturer info and courses they manage
    lecturer_courses = []
    if hasattr(current_user, 'lecturer_profile'):
        lecturer_courses = Course.query.join(Department).filter(
            Department.id == current_user.lecturer_profile.department_id
        ).all()

    return render_template(
        "dashboard.html",
        lecturer=current_user,
        courses=lecturer_courses
    )

# ----------------------
# Attendance session controls (dummy placeholders)
# ----------------------
@main_bp.route("/attendance/start/<int:course_id>")
@login_required
def start_attendance(course_id):
    course = Course.query.get(course_id)
    if not course:
        flash("Course not found.", "danger")
        return redirect(url_for("main_bp.dashboard"))
    # Logic to start attendance session (to be implemented)
    flash(f"Attendance session started for {course.name}", "success")
    return redirect(url_for("main_bp.dashboard"))

@main_bp.route("/attendance/stop/<int:course_id>")
@login_required
def stop_attendance(course_id):
    course = Course.query.get(course_id)
    if not course:
        flash("Course not found.", "danger")
        return redirect(url_for("main_bp.dashboard"))
    # Logic to stop attendance session (to be implemented)
    flash(f"Attendance session stopped for {course.name}", "info")
    return redirect(url_for("main_bp.dashboard"))

# ----------------------
# Analytics view
# ----------------------
@main_bp.route("/analytics")
@login_required
def analytics():
    # Example: fetch students and attendance for charts
    students = Student.query.all()
    return render_template(
        "analytics.html",
        students=students
    )

# ----------------------
# Communications / announcements
# ----------------------
@main_bp.route("/communications")
@login_required
def communications():
    # Placeholder: list of announcements
    announcements = []  # Could be fetched from a table in future
    return render_template(
        "communications.html",
        announcements=announcements
    )
