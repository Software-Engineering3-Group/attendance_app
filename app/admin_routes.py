from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, jsonify
)
from flask_login import login_required, current_user
from functools import wraps
from app.models import (
    db, Faculty, Department, Module,
    LecturerAssignment, Lecturer
)

# -------------------------------
# Blueprint Configuration
# -------------------------------
admin_bp = Blueprint(
    "admin_bp",
    __name__,
    template_folder="app/templates"
)

# -------------------------------
# Helper: Admin-only Access Decorator
# -------------------------------
def admin_required(func):
    """Restrict routes to admin users only."""
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Access denied: Admins only.", "danger")
            return redirect(url_for("auth_bp.admin_login"))
        return func(*args, **kwargs)
    return decorated_function


# -------------------------------
# Admin Dashboard
# -------------------------------
@admin_bp.route("/admin/dashboard")
@login_required
@admin_required
def dashboard():
    """Render admin dashboard with lecturers and assignments."""
    try:
        lecturers = Lecturer.query.join(Lecturer.user).all()
        faculties = Faculty.query.all()
        departments = Department.query.all()
        modules = Module.query.all()
        assignments = LecturerAssignment.query.order_by(LecturerAssignment.assigned_at.desc()).all()
    except Exception as e:
        flash(f"Error loading dashboard: {str(e)}", "danger")
        lecturers, faculties, departments, modules, assignments = [], [], [], [], []

    return render_template(
        "admin_dashboard.html",
        admin=current_user,
        lecturers=lecturers,
        faculties=faculties,
        departments=departments,
        modules=modules,
        assignments=assignments
    )


# -------------------------------
# Assign Lecturer to Module (many-to-many)
# -------------------------------
@admin_bp.route("/admin/assign_lecturer", methods=["POST"])
@login_required
@admin_required
def assign_lecturer():
    """Assign a lecturer to a faculty, department, and module (without course)."""
    lecturer_id = request.form.get("lecturer_id")
    faculty_id = request.form.get("faculty_id")
    department_id = request.form.get("department_id")
    module_id = request.form.get("module_id")

    if not all([lecturer_id, faculty_id, department_id, module_id]):
        flash("All fields are required to assign a lecturer.", "warning")
        return redirect(url_for("admin_bp.dashboard"))

    # Prevent duplicate assignments
    existing_assignment = LecturerAssignment.query.filter_by(
        lecturer_id=lecturer_id, module_id=module_id
    ).first()

    if existing_assignment:
        flash("This lecturer is already assigned to the selected module.", "warning")
        return redirect(url_for("admin_bp.dashboard"))

    try:
        # Create a new assignment (course_id handled internally)
        module = Module.query.get(module_id)

        assignment = LecturerAssignment(
            lecturer_id=lecturer_id,
            faculty_id=faculty_id,
            department_id=department_id,
            course_id=module.course_id,  # maintain backend relationship
            module_id=module_id
        )
        db.session.add(assignment)
        db.session.commit()
        flash("Lecturer successfully assigned to module!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error assigning lecturer: {str(e)}", "danger")

    return redirect(url_for("admin_bp.dashboard"))


# -------------------------------
# Remove Lecturer Assignment
# -------------------------------
@admin_bp.route("/admin/remove_assignment/<int:assignment_id>")
@login_required
@admin_required
def remove_assignment(assignment_id):
    """Remove a lecturer-module assignment."""
    assignment = LecturerAssignment.query.get_or_404(assignment_id)
    try:
        db.session.delete(assignment)
        db.session.commit()
        flash("Lecturer assignment removed successfully.", "info")
    except Exception as e:
        db.session.rollback()
        flash(f"Error removing assignment: {str(e)}", "danger")

    return redirect(url_for("admin_bp.dashboard"))


# -------------------------------
# Dynamic Dropdown Routes (AJAX)
# -------------------------------
@admin_bp.route("/admin/get_departments/<int:faculty_id>")
@login_required
@admin_required
def get_departments(faculty_id):
    """Return all departments under a faculty."""
    departments = Department.query.filter_by(faculty_id=faculty_id).all()
    return jsonify([{"id": d.id, "name": d.name} for d in departments])


@admin_bp.route("/admin/get_modules/<int:department_id>")
@login_required
@admin_required
def get_modules(department_id):
    """Return all modules available under a department."""
    modules = (
        Module.query.join(Module.course)
        .join(Module.course.department)
        .filter(Module.course.department_id == department_id)
        .all()
    )
    return jsonify([{"id": m.id, "name": m.name} for m in modules])
