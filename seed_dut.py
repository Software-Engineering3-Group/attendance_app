# seed_dut.py
from app import create_app
from app.models import db, Department, Course, Module

app = create_app()

with app.app_context():
    # example list based on DUT faculties (short list)
    departments = [
        ("Accounting & Informatics", [
            ("Bachelor of Information and Communications Technology", ["Programming I", "Databases I", "Networks I"]),
            ("Diploma in Accounting", ["Financial Accounting I", "Management Accounting"])
        ]),
        ("Applied Sciences", [
            ("Bachelor of Applied Science in Biotechnology", ["Intro to Biotechnology", "Microbiology"]),
        ]),
        ("Engineering & the Built Environment", [
            ("Bachelor of Engineering: Electrical", ["Engineering Maths I", "Circuit Theory"]),
        ]),
        ("Health Sciences", [
            ("Bachelor of Health Sciences in Nursing", ["Anatomy", "Physiology"]),
        ]),
        ("Management Sciences", [
            ("Bachelor of Business Administration", ["Principles of Management", "Marketing 101"]),
        ]),
        ("Arts & Design", [
            ("Bachelor of Arts", ["Cornerstone 101", "English for Tertiary Studies"]),
        ]),
    ]

    for dept_name, courses in departments:
        d = Department.query.filter_by(name=dept_name).first()
        if not d:
            d = Department(name=dept_name)
            db.session.add(d)
            db.session.flush()
        for course_name, modules in courses:
            c = Course(name=course_name, department_id=d.id)
            db.session.add(c)
            db.session.flush()
            for mname in modules:
                mm = Module(name=mname, course_id=c.id)
                db.session.add(mm)
    db.session.commit()
    print("Seeded DUT sample departments/courses/modules.")
