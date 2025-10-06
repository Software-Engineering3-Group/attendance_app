from flask import Blueprint, render_template, jsonify
from .models import db, Faculty, Department, Course, Module
from flask_login import login_required

courses_bp = Blueprint("courses_bp", __name__)

# ----------------------
# Web page: list courses and hierarchy
# ----------------------
@courses_bp.route("/")
@login_required
def list_courses():
    faculties = Faculty.query.order_by(Faculty.name).all()
    return render_template("courses.html", faculties=faculties)

# ----------------------
# API: Get departments by faculty
# ----------------------
@courses_bp.route("/api/departments/<int:faculty_id>")
def api_departments(faculty_id):
    depts = Department.query.filter_by(faculty_id=faculty_id).order_by(Department.name).all()
    result = [{"id": d.id, "name": d.name} for d in depts] if depts else []
    return jsonify(result)

# ----------------------
# API: Get courses by department
# ----------------------
@courses_bp.route("/api/courses/<int:dept_id>")
def api_courses(dept_id):
    courses = Course.query.filter_by(department_id=dept_id).order_by(Course.name).all()
    result = [{"id": c.id, "name": c.name, "semester": c.semester, "year": c.year} for c in courses] if courses else []
    return jsonify(result)

# ----------------------
# API: Get modules by course
# ----------------------
@courses_bp.route("/api/modules/<int:course_id>")
def api_modules(course_id):
    modules = Module.query.filter_by(course_id=course_id).order_by(Module.name).all()
    result = [{"id": m.id, "name": m.name} for m in modules] if modules else []
    return jsonify(result)

@courses_bp.route("/manage-marks")
@login_required
def manage_marks():
    """Temporary placeholder for managing student marks."""
    return render_template("manage_marks.html")