from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ------------------ User Base ------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    contact = db.Column(db.String(80), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'student', 'lecturer', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ------------------ Extended User Models ------------------
class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    student_number = db.Column(db.String(50), unique=True, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculties.id"), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=True)
    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=True)
    face_encoding = db.Column(db.Text, nullable=True)

    user = db.relationship("User", backref=db.backref("student_profile", uselist=False))

class Lecturer(db.Model):
    __tablename__ = "lecturers"
    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    lecturer_id = db.Column(db.String(50), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True)

    user = db.relationship("User", backref=db.backref("lecturer_profile", uselist=False))

# ------------------ Faculty & Academic Models ------------------
class Faculty(db.Model):
    __tablename__ = "faculties"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    departments = db.relationship("Department", backref="faculty", lazy=True)
    students = db.relationship("Student", backref="faculty", lazy=True)

class Department(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculties.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    courses = db.relationship("Course", backref="department", lazy=True)
    students = db.relationship("Student", backref="department", lazy=True)
    lecturers = db.relationship("Lecturer", backref="department", lazy=True)

class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    semester = db.Column(db.String(50), nullable=True)
    year = db.Column(db.Integer, nullable=True)

    modules = db.relationship("Module", backref="course", lazy=True)
    students = db.relationship("Student", backref="course", lazy=True)

class Module(db.Model):
    __tablename__ = "modules"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    students = db.relationship("Student", backref="module", lazy=True)
    attendance_sessions = db.relationship("AttendanceSession", backref="module", lazy=True)
    marks = db.relationship("Mark", backref="module", lazy=True)

# ------------------ Attendance ------------------
class AttendanceSession(db.Model):
    __tablename__ = "attendance_sessions"
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=False)
    lecturer_id = db.Column(db.Integer, db.ForeignKey("lecturers.id"), nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    records = db.relationship("AttendanceRecord", backref="session", lazy=True)

class AttendanceRecord(db.Model):
    __tablename__ = "attendance_records"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("attendance_sessions.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="present")

    student = db.relationship("Student", backref=db.backref("attendance_records", lazy=True))

# ------------------ Marks ------------------
class Mark(db.Model):
    __tablename__ = "marks"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=False)
    mark = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", backref=db.backref("marks", lazy=True))

# ------------------ Announcements & Resources ------------------
class Announcement(db.Model):
    __tablename__ = "announcements"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    uploader = db.relationship("User", backref=db.backref("announcements", lazy=True))
