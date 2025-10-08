from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import random
import string

db = SQLAlchemy()

# ------------------------------------------------------------
# Helper: Generate unique employee IDs
# ------------------------------------------------------------
def generate_employee_id(prefix="DUT-L"):
    suffix = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{suffix}"

# ------------------------------------------------------------
# Base User Model
# ------------------------------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="student")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User {self.full_name} ({self.role})>"

# ------------------------------------------------------------
# Faculty Model
# ------------------------------------------------------------
class Faculty(db.Model):
    __tablename__ = "faculties"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    departments = db.relationship("Department", backref="faculty", lazy=True)
    lecturer_assignments = db.relationship("LecturerAssignment", back_populates="faculty", lazy=True)

    def __repr__(self):
        return f"<Faculty {self.name}>"

# ------------------------------------------------------------
# Department Model
# ------------------------------------------------------------
class Department(db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculties.id"), nullable=False)

    courses = db.relationship("Course", backref="department", lazy=True)
    lecturer_assignments = db.relationship("LecturerAssignment", back_populates="department", lazy=True)

    def __repr__(self):
        return f"<Department {self.name}>"

# ------------------------------------------------------------
# Course Model
# ------------------------------------------------------------
class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)

    modules = db.relationship("Module", backref="course", lazy=True)

    def __repr__(self):
        return f"<Course {self.name}>"

# ------------------------------------------------------------
# Module Model
# ------------------------------------------------------------
class Module(db.Model):
    __tablename__ = "modules"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    lecturer_assignments = db.relationship("LecturerAssignment", back_populates="module", lazy=True)
    attendance_sessions = db.relationship("AttendanceSession", back_populates="module", lazy=True)

    def __repr__(self):
        return f"<Module {self.name}>"

# ------------------------------------------------------------
# Lecturer Model
# ------------------------------------------------------------
class Lecturer(db.Model):
    __tablename__ = "lecturers"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False, default=lambda: generate_employee_id())
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculties.id"), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)

    user = db.relationship("User", backref=db.backref("lecturer_profile", uselist=False))
    faculty = db.relationship("Faculty", backref="lecturers")
    department = db.relationship("Department", backref="lecturers")

    # ✅ Lecturer can have MANY modules through LecturerAssignment
    lecturer_assignments = db.relationship(
        "LecturerAssignment",
        back_populates="lecturer",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Lecturer {self.employee_id} - {self.user.full_name}>"

# ------------------------------------------------------------
# Admin Model
# ------------------------------------------------------------
class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    employee_id = db.Column(db.String(50), unique=True, nullable=False, default=lambda: generate_employee_id(prefix="DUT-A"))

    user = db.relationship("User", backref=db.backref("admin_profile", uselist=False))

    def __repr__(self):
        return f"<Admin {self.employee_id} - {self.user.full_name}>"

# ------------------------------------------------------------
# Lecturer Assignment (Many-to-Many Bridge)
# ------------------------------------------------------------
class LecturerAssignment(db.Model):
    __tablename__ = "lecturer_assignments"

    id = db.Column(db.Integer, primary_key=True)
    lecturer_id = db.Column(db.Integer, db.ForeignKey("lecturers.id"), nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculties.id"), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    visible = db.Column(db.Boolean, default=True)

    lecturer = db.relationship("Lecturer", back_populates="lecturer_assignments")
    faculty = db.relationship("Faculty", back_populates="lecturer_assignments")
    department = db.relationship("Department", back_populates="lecturer_assignments")
    module = db.relationship("Module", back_populates="lecturer_assignments")

    def __repr__(self):
        return f"<Assignment LECTURER {self.lecturer_id} → MODULE {self.module_id}>"

# ------------------------------------------------------------
# Student Model
# ------------------------------------------------------------
class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    student_number = db.Column(db.String(50), unique=True, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey("faculties.id"))
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"))
    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"))
    face_encoding = db.Column(db.Text, nullable=True)

    user = db.relationship("User", backref=db.backref("student_profile", uselist=False))
    attendance_records = db.relationship(
        "AttendanceRecord",
        back_populates="student",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Student {self.student_number} - {self.user.full_name}>"

# ------------------------------------------------------------
# Attendance Session
# ------------------------------------------------------------
class AttendanceSession(db.Model):
    __tablename__ = "attendance_sessions"

    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey("modules.id"), nullable=False)
    session_date = db.Column(db.DateTime, default=datetime.utcnow)

    module = db.relationship("Module", back_populates="attendance_sessions")
    attendance_records = db.relationship("AttendanceRecord", back_populates="session", lazy=True)

    def __repr__(self):
        return f"<Session {self.module.name} on {self.session_date.strftime('%Y-%m-%d')}>"

# ------------------------------------------------------------
# Attendance Record
# ------------------------------------------------------------
class AttendanceRecord(db.Model):
    __tablename__ = "attendance_records"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("attendance_sessions.id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="absent")
    marked_at = db.Column(db.DateTime, default=datetime.utcnow)
    attendance_marks = db.Column(db.Integer, default=0)

    session = db.relationship("AttendanceSession", back_populates="attendance_records")
    student = db.relationship("Student", back_populates="attendance_records")

    def __repr__(self):
        return f"<Attendance Student {self.student_id} - {self.status} - Marks {self.attendance_marks}>"
