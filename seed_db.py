import os
import datetime
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'college_erp.settings')
django.setup()

from accounts.models import User
from departments.models import Department, ClassroomAlert, TimetableSlot
from students.models import Student
from faculty.models import Faculty

def seed():
    print("Seeding database...")
    
    # 1. Create admin user
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@smart.erp',
            password='admin123',
            role='ADMIN'
        )
        print("Superuser created: username='admin', password='admin123'")
    else:
        admin_user = User.objects.get(username='admin')
        print("Superuser already exists.")

    # 2. Create departments
    depts_data = [
        {"name": "Computer Science & Engineering", "code": "CSE", "description": "Branch of coding, algorithms, and computing systems"},
        {"name": "Electrical Engineering", "code": "EE", "description": "Branch of power grid, electronics, and digital processors"},
        {"name": "Mechanical Engineering", "code": "ME", "description": "Branch of fluid mechanics, thermodynamics, and robotics"},
    ]
    
    depts = []
    for d in depts_data:
        dept, created = Department.objects.get_or_create(
            code=d["code"],
            defaults={"name": d["name"], "description": d["description"]}
        )
        depts.append(dept)
        if created:
            print(f"Department created: {dept}")

    # 3. Create mock faculty user & profile
    faculty_user_data = [
        {"username": "prof_sharma", "email": "sharma@smart.erp", "first_name": "Rohan", "last_name": "Sharma", "employee_id": "FAC001", "subject": "Data Structures", "dept": depts[0]},
        {"username": "prof_patel", "email": "patel@smart.erp", "first_name": "Priya", "last_name": "Patel", "employee_id": "FAC002", "subject": "Digital Electronics", "dept": depts[1]}
    ]
    
    faculties = []
    for f in faculty_user_data:
        if not User.objects.filter(username=f["username"]).exists():
            user = User.objects.create_user(
                username=f["username"],
                email=f["email"],
                password="password123",
                role="FACULTY"
            )
            faculty = Faculty.objects.create(
                user=user,
                first_name=f["first_name"],
                last_name=f["last_name"],
                employee_id=f["employee_id"],
                subject=f["subject"],
                department=f["dept"]
            )
            faculties.append(faculty)
            print(f"Faculty registered: {faculty}")
        else:
            faculties.append(Faculty.objects.get(employee_id=f["employee_id"]))

    # 4. Create mock student user & profile
    student_user_data = [
        {
            "username": "student_amit", "email": "amit@smart.erp", "first_name": "Amit", "last_name": "Kumar",
            "roll_number": "CS-2026-992", "dept": depts[0],
            "attendance": 92.4, "fee_amount": 15000.00, "fee_status": "PAID",
            "gpa": 9.1, "assessment": "All Assignments: Submitted | Midterms: Cleared (91%)"
        },
        {
            "username": "student_sneha", "email": "sneha@smart.erp", "first_name": "Sneha", "last_name": "Reddy",
            "roll_number": "EE-2026-102", "dept": depts[1],
            "attendance": 78.5, "fee_amount": 15000.00, "fee_status": "PENDING",
            "gpa": 8.4, "assessment": "Assignment 2: Pending | Midterms: Cleared (82%)"
        },
        {
            "username": "student_kabir", "email": "kabir@smart.erp", "first_name": "Kabir", "last_name": "Bose",
            "roll_number": "ME-2026-054", "dept": depts[2],
            "attendance": 68.2, "fee_amount": 15000.00, "fee_status": "OVERDUE",
            "gpa": 7.2, "assessment": "Term Project: Under Review | Midterms: Cleared (70%)"
        },
    ]
    
    for s in student_user_data:
        if not User.objects.filter(username=s["username"]).exists():
            user = User.objects.create_user(
                username=s["username"],
                email=s["email"],
                password="password123",
                role="STUDENT"
            )
            student = Student.objects.create(
                user=user,
                first_name=s["first_name"],
                last_name=s["last_name"],
                roll_number=s["roll_number"],
                department=s["dept"],
                attendance_percentage=s["attendance"],
                semester_fee_amount=s["fee_amount"],
                semester_fee_status=s["fee_status"],
                semester_result_gpa=s["gpa"],
                assessment_status=s["assessment"]
            )
            print(f"Student registered: {student}")

    # 5. Create mock Classroom Alerts
    alerts_data = [
        {
            "title": "Data Structures Practical Lab Relocated",
            "room_number": "Lab 304 (3rd Floor)",
            "subject": "Data Structures",
            "alert_type": "ROOM_CHANGE",
            "priority": "HIGH",
            "message": "Today's 02:00 PM Data Structures practical lab has been moved from Lab 101 to Lab 304 due to hardware maintenance.",
            "department": depts[0],
            "created_by_faculty": faculties[0],
            "created_by_name": f"Prof. {faculties[0].first_name} {faculties[0].last_name}"
        },
        {
            "title": "Digital Electronics Extra Class Scheduled",
            "room_number": "LH-02",
            "subject": "Digital Electronics",
            "alert_type": "SCHEDULE_CHANGE",
            "priority": "MEDIUM",
            "message": "An extra tutorial session for Digital Electronics will take place in LH-02 tomorrow at 11:00 AM.",
            "department": depts[1],
            "created_by_faculty": faculties[1],
            "created_by_name": f"Prof. {faculties[1].first_name} {faculties[1].last_name}"
        },
        {
            "title": "Fluid Mechanics Lecture Cancelled",
            "room_number": "Room 201",
            "subject": "Fluid Mechanics",
            "alert_type": "CANCELLATION",
            "priority": "HIGH",
            "message": "The Fluid Mechanics morning lecture is cancelled today due to faculty emergency. Self-study in library.",
            "department": depts[2],
            "created_by_faculty": None,
            "created_by_name": "System Admin"
        }
    ]

    for a in alerts_data:
        if not ClassroomAlert.objects.filter(title=a["title"]).exists():
            alert = ClassroomAlert.objects.create(**a)
            print(f"Classroom alert created: {alert}")

    # 6. Create mock Timetable Slots
    days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']
    timetable_data = [
        # CSE Slots
        {"department": depts[0], "subject": "Data Structures", "faculty": faculties[0], "day_of_week": "MONDAY", "start_time": datetime.time(9, 0), "end_time": datetime.time(10, 0), "room_number": "Room 101", "semester_or_year": "Semester 3"},
        {"department": depts[0], "subject": "Operating Systems", "faculty": faculties[0], "day_of_week": "MONDAY", "start_time": datetime.time(10, 15), "end_time": datetime.time(11, 15), "room_number": "Room 101", "semester_or_year": "Semester 3"},
        {"department": depts[0], "subject": "Algorithms Lab", "faculty": faculties[0], "day_of_week": "TUESDAY", "start_time": datetime.time(14, 0), "end_time": datetime.time(16, 0), "room_number": "Lab 304", "semester_or_year": "Semester 3"},
        {"department": depts[0], "subject": "Computer Networks", "faculty": faculties[0], "day_of_week": "WEDNESDAY", "start_time": datetime.time(11, 30), "end_time": datetime.time(12, 30), "room_number": "Room 102", "semester_or_year": "Semester 3"},
        {"department": depts[0], "subject": "Database Systems", "faculty": faculties[0], "day_of_week": "THURSDAY", "start_time": datetime.time(9, 0), "end_time": datetime.time(10, 0), "room_number": "Room 101", "semester_or_year": "Semester 3"},
        {"department": depts[0], "subject": "Software Engineering", "faculty": faculties[0], "day_of_week": "FRIDAY", "start_time": datetime.time(10, 15), "end_time": datetime.time(11, 15), "room_number": "LH-01", "semester_or_year": "Semester 3"},

        # EE Slots
        {"department": depts[1], "subject": "Digital Electronics", "faculty": faculties[1], "day_of_week": "MONDAY", "start_time": datetime.time(10, 0), "end_time": datetime.time(11, 0), "room_number": "LH-02", "semester_or_year": "Semester 3"},
        {"department": depts[1], "subject": "Power Systems", "faculty": faculties[1], "day_of_week": "TUESDAY", "start_time": datetime.time(9, 0), "end_time": datetime.time(10, 0), "room_number": "LH-02", "semester_or_year": "Semester 3"},
        {"department": depts[1], "subject": "Control Systems Lab", "faculty": faculties[1], "day_of_week": "WEDNESDAY", "start_time": datetime.time(14, 0), "end_time": datetime.time(16, 0), "room_number": "EE-Lab-1", "semester_or_year": "Semester 3"},
        {"department": depts[1], "subject": "Microprocessors", "faculty": faculties[1], "day_of_week": "FRIDAY", "start_time": datetime.time(11, 0), "end_time": datetime.time(12, 0), "room_number": "LH-02", "semester_or_year": "Semester 3"},
    ]

    for t in timetable_data:
        if not TimetableSlot.objects.filter(department=t["department"], day_of_week=t["day_of_week"], subject=t["subject"], start_time=t["start_time"]).exists():
            slot = TimetableSlot.objects.create(**t)
            print(f"Timetable slot created: {slot}")

    print("Seeding database complete!")

if __name__ == '__main__':
    seed()
