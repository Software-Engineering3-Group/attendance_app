from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import Faculty, Department, Course, Module, User, db

main_bp = Blueprint(
    "main_bp",
    __name__,
    template_folder="app/templates"
)

# ----------------------
# Landing page
# ----------------------
@main_bp.route("/")
def landing():
    return render_template("landing.html")


# ----------------------
# Admin dashboard
# ----------------------
@main_bp.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for("main_bp.dashboard"))

    # Admin can view all lecturers and academic structures
    lecturers = User.query.filter_by(role="lecturer").all()
    faculties = Faculty.query.all()
    departments = Department.query.all()
    courses = Course.query.all()
    modules = Module.query.all()

    return render_template(
        "admin_dashboard.html",
        admin=current_user,
        lecturers=lecturers,
        faculties=faculties,
        departments=departments,
        courses=courses,
        modules=modules
    )


# ----------------------
# Lecturer dashboard
# ----------------------
@main_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "admin":
        return redirect(url_for("main_bp.admin_dashboard"))

    if current_user.role != "lecturer":
        flash("Access denied. Lecturers only.", "danger")
        return redirect(url_for("main_bp.landing"))

    # Fetch lecturer's assigned modules (from admin assignment)
    assigned_modules = Module.query.filter(
        Module.id.in_(
            db.session.query(Module.id)
            .join(Course)
            .join(Department)
            .join(Faculty)
        )
    ).all()

    return render_template(
        "dashboard.html",
        lecturer=current_user,
        modules=assigned_modules
    )


# ----------------------
# Attendance session controls
# ----------------------
@main_bp.route("/attendance/start/<int:module_id>")
@login_required
def start_attendance(module_id):
    if current_user.role != "lecturer":
        flash("Access denied. Only lecturers can start attendance.", "danger")
        return redirect(url_for("main_bp.dashboard"))

    module = Module.query.get(module_id)
    if not module:
        flash("Module not found.", "danger")
        return redirect(url_for("main_bp.dashboard"))

    # TODO: Implement session start logic
    flash(f"Attendance session started for {module.name}", "success")
    return redirect(url_for("main_bp.dashboard"))


@main_bp.route("/attendance/stop/<int:module_id>")
@login_required
def stop_attendance(module_id):
    if current_user.role != "lecturer":
        flash("Access denied. Only lecturers can stop attendance.", "danger")
        return redirect(url_for("main_bp.dashboard"))

    module = Module.query.get(module_id)
    if not module:
        flash("Module not found.", "danger")
        return redirect(url_for("main_bp.dashboard"))

    # TODO: Implement session stop logic
    flash(f"Attendance session stopped for {module.name}", "info")
    return redirect(url_for("main_bp.dashboard"))


# ----------------------
# Analytics view
# ----------------------
@main_bp.route("/analytics")
@login_required
def analytics():
    if current_user.role != "lecturer":
        flash("Access denied. Only lecturers can view analytics.", "danger")
        return redirect(url_for("main_bp.dashboard"))

    # Fetch all students (filtered by role)
    students = User.query.filter_by(role="student").all()

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
    announcements = []  # Will later be fetched from Announcement model
    return render_template(
        "communications.html",
        announcements=announcements
    )

from flask import request
from datetime import datetime
from .models import LecturerAssignment

@main_bp.route("/admin/assign_lecturer", methods=["POST"])
@login_required
def assign_lecturer():
    if current_user.role != "admin":
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for("main_bp.admin_dashboard"))

    lecturer_id = request.form.get("lecturer_id")
    faculty_id = request.form.get("faculty_id")
    department_id = request.form.get("department_id")
    course_id = request.form.get("course_id")
    module_id = request.form.get("module_id")

    if not all([lecturer_id, faculty_id, department_id, course_id, module_id]):
        flash("All fields are required.", "danger")
        return redirect(url_for("main_bp.admin_dashboard"))

    # Prevent duplicate assignments
    existing = LecturerAssignment.query.filter_by(
        lecturer_id=lecturer_id, module_id=module_id
    ).first()

    if existing:
        flash("This lecturer is already assigned to that module.", "warning")
        return redirect(url_for("main_bp.admin_dashboard"))

    # Create new assignment
    new_assignment = LecturerAssignment(
        lecturer_id=lecturer_id,
        faculty_id=faculty_id,
        department_id=department_id,
        course_id=course_id,
        module_id=module_id,
        assigned_at=datetime.utcnow()
    )

    db.session.add(new_assignment)
    db.session.commit()

    flash("Lecturer assigned successfully!", "success")
    return redirect(url_for("main_bp.admin_dashboard"))
