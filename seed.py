## seed.py
from app import create_app
from app.models import db, Department, Course, Module

# create the Flask app context
app = create_app()

with app.app_context():
    # clear existing (optional, uncomment if you want a clean slate)
    # db.drop_all()
    # db.create_all()

    # ----------------------
    # DUT Departments, Courses, Modules
    # ----------------------
    data = {
        "Information & Communication Technology": {
            "Information Technology": [
                "Programming 1", "Programming 2", "Databases", "Networking", "Software Engineering"
            ],
            "Computer Systems": [
                "Electronics", "Operating Systems", "Networking", "Embedded Systems"
            ],
        },
        "Accounting & Informatics": {
            "Financial Accounting": [
                "Accounting 1", "Accounting 2", "Taxation", "Auditing"
            ],
            "Business Information Systems": [
                "Systems Analysis", "Business Processes", "ERP Systems"
            ],
        },
        "Engineering & Built Environment": {
            "Civil Engineering": [
                "Engineering Mathematics", "Structural Engineering", "Geotechnics"
            ],
            "Electrical Engineering": [
                "Circuit Theory", "Power Systems", "Control Systems"
            ],
        },
    }

    # insert departments, courses, modules
    for dept_name, courses in data.items():
        dept = Department.query.filter_by(name=dept_name).first()
        if not dept:
            dept = Department(name=dept_name)
            db.session.add(dept)
            db.session.commit()

        for course_name, modules in courses.items():
            course = Course.query.filter_by(name=course_name, department_id=dept.id).first()
            if not course:
                course = Course(name=course_name, department_id=dept.id)
                db.session.add(course)
                db.session.commit()

            for module_name in modules:
                mod = Module.query.filter_by(name=module_name, course_id=course.id).first()
                if not mod:
                    mod = Module(name=module_name, course_id=course.id)
                    db.session.add(mod)

    db.session.commit()
    print("✅ DUT departments, courses, and modules have been seeded!")
