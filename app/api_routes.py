# app/api_routes.py
from flask import Blueprint, jsonify
from .models import Faculty, Department, Course, Module

api_bp = Blueprint('api_bp', __name__)

@api_bp.route('/api/faculties/<int:faculty_id>/departments')
def get_departments(faculty_id):
    departments = Department.query.filter_by(faculty_id=faculty_id).all()
    return jsonify([{"id": d.id, "name": d.name} for d in departments])

@api_bp.route('/api/departments/<int:department_id>/courses')
def get_courses(department_id):
    courses = Course.query.filter_by(department_id=department_id).all()
    return jsonify([{"id": c.id, "name": c.name} for c in courses])

@api_bp.route('/api/courses/<int:course_id>/modules')
def get_modules(course_id):
    modules = Module.query.filter_by(course_id=course_id).all()
    return jsonify([{"id": m.id, "name": m.name} for m in modules])
