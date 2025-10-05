from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import db, Module, AttendanceSession, AttendanceRecord, Student

attendance_bp = Blueprint("attendance_bp", __name__)

# ----------------------
# Start attendance session (web)
# ----------------------
@attendance_bp.route("/start", methods=["GET", "POST"])
@login_required
def start_session():
    if request.method == "POST":
        module_id = request.form.get("module_id")
        if not module_id:
            flash("Please select a module", "danger")
            return redirect(url_for("attendance_bp.start_session"))

        session = AttendanceSession(module_id=module_id, lecturer_id=current_user.id)
        db.session.add(session)
        db.session.commit()

        flash("Attendance session started", "success")
        return redirect(url_for("attendance_bp.monitor", session_id=session.id))

    # List modules for current lecturer
    if hasattr(current_user, "lecturer_profile"):
        modules = Module.query.join(Module.course).join(Module.course.department)\
            .filter(current_user.lecturer_profile.department_id == Module.course.department_id)\
            .all()
    else:
        modules = []

    return render_template("attendance_monitor.html", modules=modules)

# ----------------------
# Monitor session (web)
# ----------------------
@attendance_bp.route("/monitor/<int:session_id>")
@login_required
def monitor(session_id):
    session = AttendanceSession.query.get_or_404(session_id)
    records = AttendanceRecord.query.filter_by(session_id=session_id)\
        .order_by(AttendanceRecord.timestamp.desc()).all()
    return render_template("attendance_monitor.html", session=session, records=records)

# ----------------------
# Stop session (web)
# ----------------------
@attendance_bp.route("/stop/<int:session_id>", methods=["POST"])
@login_required
def stop_session(session_id):
    session = AttendanceSession.query.get_or_404(session_id)
    session.is_active = False
    session.ended_at = db.func.now()
    db.session.commit()
    flash("Attendance session stopped", "info")
    return redirect(url_for("main_bp.dashboard"))

# ----------------------
# API: Student posts attendance (mobile)
# ----------------------
@attendance_bp.route("/api/record", methods=["POST"])
@jwt_required()
def api_record_attendance():
    user_id = get_jwt_identity()  # mobile user ID
    data = request.get_json() or {}
    session_id = data.get("session_id")
    student_id = data.get("student_id")  # link to Student.id

    if not session_id or not student_id:
        return jsonify({"msg":"Missing required fields"}), 400

    # Prevent duplicate attendance records
    existing = AttendanceRecord.query.filter_by(session_id=session_id, student_id=student_id).first()
    if existing:
        return jsonify({"msg":"Attendance already recorded"}), 409

    rec = AttendanceRecord(session_id=session_id, student_id=student_id, status="present")
    db.session.add(rec)
    db.session.commit()
    return jsonify({"msg":"Attendance recorded successfully"}), 201

# ----------------------
# API: Get session records (dashboard polling)
# ----------------------
@attendance_bp.route("/api/session/<int:session_id>/records")
@login_required
def api_session_records(session_id):
    records = AttendanceRecord.query.filter_by(session_id=session_id)\
        .order_by(AttendanceRecord.timestamp.desc()).all()
    output = []
    for r in records:
        student = Student.query.get(r.student_id)
        output.append({
            "student_name": student.user.full_name if student else "Unknown",
            "student_number": student.student_number if student else "Unknown",
            "timestamp": r.timestamp.isoformat(),
            "status": r.status
        })
    return jsonify(output)
