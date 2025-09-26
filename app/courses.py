from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from .models import db, Department, Course, Module
from flask_login import login_required

courses_bp = Blueprint("courses_bp", __name__)

@courses_bp.route("/")
@login_required
def list_courses():
    departments = Department.query.order_by(Department.name).all()
    return render_template("courses.html", departments=departments)

@courses_bp.route("/add_course", methods=["POST"])
@login_required
def add_course():
    name = request.form.get("course_name")
    dept_id = request.form.get("department_id")
    if not name or not dept_id:
        flash("Missing fields", "danger")
    else:
        c = Course(name=name, department_id=int(dept_id))
        db.session.add(c); db.session.commit()
        flash("Course added", "success")
    return redirect(url_for("courses_bp.list_courses"))

@courses_bp.route("/add_module", methods=["POST"])
@login_required
def add_module():
    name = request.form.get("module_name")
    course_id = request.form.get("course_id")
    if not name or not course_id:
        flash("Missing fields", "danger")
    else:
        m = Module(name=name, course_id=int(course_id))
        db.session.add(m); db.session.commit()
        flash("Module added", "success")
    return redirect(url_for("courses_bp.list_courses"))

# API to fetch modules by course
@courses_bp.route("/api/course/<int:course_id>/modules")
def api_course_modules(course_id):
    mods = Module.query.filter_by(course_id=course_id).all()
    return jsonify([{"id":m.id,"name":m.name} for m in mods])
