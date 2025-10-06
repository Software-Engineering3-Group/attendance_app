from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Faculty, Department, Course, Module, LecturerAssignment, User

admin_bp = Blueprint(
    "admin_bp",
    __name__,
    template_folder="app/templates"
)

# -------------------------------
# Helper: Ensure only admin users can access
# -------------------------------
def admin_required(func):
    from functools import wraps
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Access denied: Admins only.", "danger")
            return redirect(url_for("main_bp.dashboard"))
        return func(*args, **kwargs)
    return decorated_function

# -------------------------------
# Admin Dashboard
# -------------------------------
@admin_bp.route("/admin/dashboard")
@login_required
@admin_required
def dashboard():
    lecturers = User.query.filter_by(role="lecturer").all()
    faculties = Faculty.query.all()
    departments = Department.query.all()
    courses = Course.query.all()
    modules = Module.query.all()
    assignments = LecturerAssignment.query.all()

    return render_template(
        "admin_dashboard.html",
        lecturers=lecturers,
        faculties=faculties,
        departments=departments,
        courses=courses,
        modules=modules,
        assignments=assignments
    )

# -------------------------------
# Assign Lecturer to Course/Module
# -------------------------------
@admin_bp.route("/admin/assign_lecturer", methods=["POST"])
@login_required
@admin_required
def assign_lecturer():
    lecturer_id = request.form.get("lecturer_id")
    faculty_id = request.form.get("faculty_id")
    department_id = request.form.get("department_id")
    course_id = request.form.get("course_id")
    module_id = request.form.get("module_id")

    # Check if already assigned
    existing = LecturerAssignment.query.filter_by(
        lecturer_id=lecturer_id,
        module_id=module_id
    ).first()

    if existing:
        flash("Lecturer is already assigned to this module.", "warning")
        return redirect(url_for("admin_bp.dashboard"))

    assignment = LecturerAssignment(
        lecturer_id=lecturer_id,
        faculty_id=faculty_id,
        department_id=department_id,
        course_id=course_id,
        module_id=module_id
    )
    db.session.add(assignment)
    db.session.commit()

    flash("Lecturer successfully assigned!", "success")
    return redirect(url_for("admin_bp.dashboard"))

# -------------------------------
# Remove Lecturer Assignment
# -------------------------------
@admin_bp.route("/admin/remove_assignment/<int:assignment_id>")
@login_required
@admin_required
def remove_assignment(assignment_id):
    assignment = LecturerAssignment.query.get(assignment_id)
    if not assignment:
        flash("Assignment not found.", "danger")
        return redirect(url_for("admin_bp.dashboard"))

    db.session.delete(assignment)
    db.session.commit()

    flash("Lecturer assignment removed successfully.", "info")
    return redirect(url_for("admin_bp.dashboard"))
# -------------------------------
# Dynamic Dropdown APIs
# -------------------------------
from flask import jsonify

@admin_bp.route("/admin/get_departments/<int:faculty_id>")
@login_required
@admin_required
def get_departments(faculty_id):
    departments = Department.query.filter_by(faculty_id=faculty_id).all()
    return jsonify([{"id": d.id, "name": d.name} for d in departments])

@admin_bp.route("/admin/get_courses/<int:department_id>")
@login_required
@admin_required
def get_courses(department_id):
    courses = Course.query.filter_by(department_id=department_id).all()
    return jsonify([{"id": c.id, "name": c.name} for c in courses])

@admin_bp.route("/admin/get_modules/<int:course_id>")
@login_required
@admin_required
def get_modules(course_id):
    modules = Module.query.filter_by(course_id=course_id).all()
    return jsonify([{"id": m.id, "name": m.name} for m in modules])
