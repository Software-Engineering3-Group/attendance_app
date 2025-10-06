from app import create_app
from app.models import db, Faculty, Department, Course, Module  # ✅ import from app.models

app = create_app()

with app.app_context():  # ✅ ensure all DB operations happen inside app context
    # Drop and recreate all tables
    db.drop_all()
    db.create_all()

    # ====== FACULTIES ======
    ict_faculty = Faculty(name="Faculty of Accounting and Informatics")
    engineering_faculty = Faculty(name="Faculty of Engineering and the Built Environment")
    health_faculty = Faculty(name="Faculty of Health Sciences")

    db.session.add_all([ict_faculty, engineering_faculty, health_faculty])
    db.session.commit()

    # ====== DEPARTMENTS ======
    ict_department = Department(name="Information & Communication Technology", faculty_id=ict_faculty.id)
    civil_department = Department(name="Civil Engineering", faculty_id=engineering_faculty.id)
    nursing_department = Department(name="Nursing Sciences", faculty_id=health_faculty.id)

    db.session.add_all([ict_department, civil_department, nursing_department])
    db.session.commit()

    # ====== COURSES ======
    it_course = Course(name="Diploma in Information Technology", department_id=ict_department.id)
    civil_course = Course(name="Diploma in Civil Engineering", department_id=civil_department.id)
    nursing_course = Course(name="Bachelor of Nursing", department_id=nursing_department.id)

    db.session.add_all([it_course, civil_course, nursing_course])
    db.session.commit()

    # ====== MODULES ======
    modules = [
        Module(name="Web Development", course_id=it_course.id),
        Module(name="Database Systems", course_id=it_course.id),
        Module(name="Software Engineering", course_id=it_course.id),
        Module(name="Structural Analysis", course_id=civil_course.id),
        Module(name="Surveying", course_id=civil_course.id),
        Module(name="Anatomy", course_id=nursing_course.id),
        Module(name="Pharmacology", course_id=nursing_course.id)
    ]

    db.session.add_all(modules)
    db.session.commit()

    print("✅ All data seeded successfully!")
