# app/api_routes.py
from flask import Blueprint, jsonify, request
from .models import Faculty, Department, Course, Module, Student, User
import numpy as np
import json

api_bp = Blueprint('api_bp', __name__)

# ---------------------- Helper ----------------------
def compare_face_encodings(stored_encoding, incoming_encoding, tolerance=0.45):
    """
    Compare a stored face encoding (NumPy array or JSON string) with an incoming encoding.
    Returns True if match, otherwise False.
    
    This version handles sign flips by using cosine similarity.
    """
    try:
        # Load stored encoding
        if isinstance(stored_encoding, str):
            stored_encoding = np.array(json.loads(stored_encoding), dtype=np.float32)
        elif isinstance(stored_encoding, list):
            stored_encoding = np.array(stored_encoding, dtype=np.float32)
        else:
            stored_encoding = stored_encoding.astype(np.float32)

        # Ensure incoming encoding is a NumPy array
        incoming_encoding = np.array(incoming_encoding, dtype=np.float32)

        # Normalize both vectors
        stored_norm = stored_encoding / np.linalg.norm(stored_encoding)
        incoming_norm = incoming_encoding / np.linalg.norm(incoming_encoding)

        # Compute cosine similarity
        cosine_sim = np.dot(stored_norm, incoming_norm)
        
        # Print for debugging
        print("Stored encoding:", stored_norm)
        print("-------------------------")
        print("Incoming encoding:", incoming_norm)
        print("Cosine similarity:", cosine_sim)

        # Check against tolerance (higher similarity = closer match)
        return cosine_sim >= (1 - tolerance)

    except Exception as e:
        print(f"Error comparing encodings: {e}")
        return False

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


@api_bp.route('/api/face/verify', methods=['POST'])
def verify_face():
    try:
        data = request.get_json()
        incoming_encoding = data.get("face_encoding")

        if not incoming_encoding:
            return jsonify({
                "match": False,
                "message": "No face encoding provided.",
                "duplicateMatch": False
            }), 400

        incoming_encoding = np.array(incoming_encoding, dtype=np.float32)
        students = Student.query.join(User).filter(Student.face_encoding.isnot(None)).all()
        print(f"Total students with face encodings: {len(students)}")

        for student in students:
            stored = student.face_encoding
            try:
                match = compare_face_encodings(stored, incoming_encoding, tolerance=0.5)  # cosine threshold
                if match:
                    return jsonify({
                        "match": True,
                        "message": f"Match found: {student.user.full_name} signed",
                        "duplicateMatch": False
                    }), 200
            except Exception as e:
                print(f"Error comparing encodings for {student.user.full_name}: {e}")
                continue

        return jsonify({
            "match": False,
            "message": "No match found.",
            "duplicateMatch": False
        }), 200

    except Exception as e:
        return jsonify({
            "match": False,
            "message": f"Server error: {str(e)}",
            "duplicateMatch": False
        }), 500

    