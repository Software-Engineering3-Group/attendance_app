from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import db, AttendanceSession, AttendanceRecord, Module
from flask_jwt_extended import jwt_required, get_jwt_identity

attendance_bp = Blueprint("attendance_bp", __name__)

# Web: start session form
@attendance_bp.route("/start", methods=["GET", "POST"])
@login_required
def start_session():
    if request.method == "POST":
        module_id = request.form.get("module_id")
        if not module_id:
            flash("Select module", "danger")
            return redirect(url_for("attendance_bp.start_session"))
        s = AttendanceSession(module_id=module_id, lecturer_id=current_user.id)
        db.session.add(s); db.session.commit()
        flash("Session started", "success")
        return redirect(url_for("attendance_bp.monitor", session_id=s.id))
    # list modules for lecturer (basic)
    modules = Module.query.all()
    return render_template("attendance_monitor.html", modules=modules)

# Web: monitor page for session (polls records)
@attendance_bp.route("/monitor/<int:session_id>")
@login_required
def monitor(session_id):
    session = AttendanceSession.query.get_or_404(session_id)
    return render_template("attendance_monitor.html", session=session)

# Web: stop session
@attendance_bp.route("/stop/<int:session_id>", methods=["POST"])
@login_required
def stop_session(session_id):
    s = AttendanceSession.query.get_or_404(session_id)
    s.ended_at = db.func.now()
    s.is_active = False
    db.session.commit()
    flash("Session stopped", "info")
    return redirect(url_for("main_bp.dashboard"))

# Mobile API: student posts attendance (JWT protected)
@attendance_bp.route("/api/record", methods=["POST"])
@jwt_required()
def api_record_attendance():
    user_id = get_jwt_identity()  # identifies mobile user (student or lecturer)
    data = request.get_json() or {}
    session_id = data.get("session_id")
    student_identifier = data.get("student_identifier")
    if not session_id or not student_identifier:
        return jsonify({"msg":"missing"}), 400
    rec = AttendanceRecord(session_id=session_id, student_identifier=student_identifier)
    db.session.add(rec); db.session.commit()
    return jsonify({"msg":"ok"}), 201

# API to get session records (for dashboard polling)
@attendance_bp.route("/api/session/<int:session_id>/records")
@login_required
def api_session_records(session_id):
    records = AttendanceRecord.query.filter_by(session_id=session_id).order_by(AttendanceRecord.timestamp.desc()).limit(200).all()
    out = [{"student_identifier":r.student_identifier,"timestamp":r.timestamp.isoformat(),"status":r.status} for r in records]
    return jsonify(out)
