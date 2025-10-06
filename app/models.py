from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import random
import string

db = SQLAlchemy()

# -------------------------
# Helper function to generate a random employee ID
# -------------------------
def generate_employee_id():
    prefix = "DUT-L"
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{suffix}"

# -------------------------
# User Model (Admin & Lecturer)
# -------------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="lecturer")  # 'admin' or 'lecturer'
    employee_id = db.Column(db.String(20), unique=True, nullable=True)
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
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True)

    user = db.relationship("User", backref=db.backref("lecturer_profile", uselist=False))

class Admin(db.Model):
    __tablename__ = "admins"
    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False)
    user = db.relationship("User", backref=db.backref("admin_profile", uselist=False))

class LecturerAssignment(db.Model):
    __tablename__ =  "lecturer_assignments"
    _table_args__ = {"extend_existing": True}

    id=db.Column(db.Integer, primary_key=True)
    #lecturer_id= db.Column(db.Integer, db.Foreignkey("lecturer.id"), nullable=False)
    faculty_id= db.Column(db.Integer, db.ForeignKey("faculties.id"), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    course_id = db.Column(db.Integer, db. ForeignKey("courses.id"), nullable=False)
    module_id= db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=False)

    assigned_at =  db.Column(db.DateTime, default=datetime.utcnow)
    lecturer = db.relationship("User", back_populates="lecturer_assignments")
    faculty = db.relationship("Faculty", back_populates="faculty_assignments")
    department = db.relationship("Department", back_populates="department_assignments")
    course = db.relationship("Course", back_populates="course_assignments")
    module = db.relationship("Module", back_populates="assignments")

# ------------------ Faculty & Academic Models ------------------
class Faculty(db.Model):
    __tablename__ = "faculties"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    departments = db.relationship("Department", backref="faculty", lazy=True)
    faculty_assignments = db.relationship("LecturerAssignment", back_populates="faculty", lazy=True)


# -------------------------
# Department Model
# -------------------------
class Department(db.Model):
    __tablename__ = "departments"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculties.id"), nullable=False)

    courses = db.relationship("Course", backref="department", lazy=True)
    department_assignments = db.relationship("LecturerAssignment", back_populates="department", lazy=True)


# -------------------------
# Course Model
# -------------------------
class Course(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)

    modules = db.relationship("Module", backref="course", lazy=True)
    course_assignments = db.relationship("LecturerAssignment", back_populates="course", lazy=True)


# -------------------------
# Module Model
# -------------------------
class Module(db.Model):
    __tablename__ = "modules"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    assignments = db.relationship("LecturerAssignment", back_populates="module", lazy=True)
    attendance_sessions = db.relationship("AttendanceSession", back_populates="module", lazy=True)


# -------------------------
# LecturerAssignment Model
# -------------------------
class LecturerAssignment(db.Model):
    __tablename__ = "lecturer_assignments"
    __table_args__ = {"extend_existing": True}

    id = db.Column(db.Integer, primary_key=True)
    lecturer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculties.id"), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    lecturer = db.relationship("User", back_populates="lecturer_assignments")
    faculty = db.relationship("Faculty", back_populates="faculty_assignments")
    department = db.relationship("Department", back_populates="department_assignments")
    course = db.relationship("Course", back_populates="course_assignments")
    module = db.relationship("Module", back_populates="assignments")


# -------------------------
# Student Model
# -------------------------
class Student(db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attendance_records = db.relationship("AttendanceRecord", back_populates="student", lazy=True)


# -------------------------
# AttendanceSession Model
# -------------------------
class AttendanceSession(db.Model):
    __tablename__ = "attendance_sessions"
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=False)
    session_date = db.Column(db.DateTime, default=datetime.utcnow)

    module = db.relationship("Module", back_populates="attendance_sessions")
    attendance_records = db.relationship("AttendanceRecord", back_populates="session", lazy=True)


# -------------------------
# AttendanceRecord Model
# -------------------------
class AttendanceRecord(db.Model):
    __tablename__ = "attendance_records"
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("attendance_sessions.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="absent")
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)

    session = db.relationship("AttendanceSession", back_populates="attendance_records")
    student = db.relationship("Student", back_populates="attendance_records")
