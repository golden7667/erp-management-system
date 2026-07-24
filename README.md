# Smart College ERP System

A premium, feature-rich college Enterprise Resource Planning (ERP) web application built using **Django** and styled with modern dark/light-themed **Bootstrap 5 / HSL tailored CSS**.

---

## 🌟 Key Features & Modules

### 1. Classroom Alerts & Room Notices (NEW)
- **Broadcast Announcements**: Faculty and Admins can broadcast real-time announcements for room relocations, class cancellations, schedule shifts, or urgent notices.
- **Categorized Priority Badges**: Priority tags (`URGENT`, `HIGH`, `MEDIUM`, `LOW`) and alert type badges (`ROOM_CHANGE`, `CANCELLATION`, `SCHEDULE_CHANGE`, `INFO`).
- **Filtering & Live Search**: Filter by alert type or department, or search by subject, room number, or notice title.
- **Dashboard Widget**: Live **Active Classroom Alerts** cards displayed prominently on both Student and Faculty dashboards.

### 2. Interactive Class Timetable & Schedule (NEW)
- **Weekly Schedule Grid**: Visual weekly timetable organized by days of the week (**Monday to Saturday**) and time slots.
- **Lecture Details**: Displays room allocations, assigned faculty teacher, subject, and time slots.
- **Today's Schedule Widget**: Shows the current day's chronological class schedule on Student and Faculty dashboards.
- **Timetable Management**: Faculty and Admins can easily add, edit, or remove timetable slots.

### 3. Attendance Marking by Roll Number (NEW)
- **Roll Number Ordering**: Student cohort list sorted strictly by **Roll Number** (`CS-2026-992`, `EE-2026-102`, etc.).
- **Quick Roll Number Search & Mark**: Top search box with Roll Number autocomplete to quickly mark a student Present (+1) or Absent with a single click.
- **Live Search Filter**: Instant client-side search filtering by Roll Number or student name.
- **Batch Attendance Switches**: Present/Absent pill radio buttons for each student roll number, with **"Mark All Present"** and **"Mark All Absent"** shortcuts.

### 4. Administration Module
- **Consolidated Dashboard**: View student registration counts, faculty allocations, branch distributions, and interactive Chart.js analytics.
- **Department Management**: Add, update, or remove departments and code tracks (e.g., CSE, EE, ME).
- **Faculty & Student Management**: Add, edit, or delete faculty/student profiles with custom photo uploads and address details.
- **Admin Profile & ID Card**: Edit administrator profile, change passwords, and view/print official **Administrator ID Card** with barcode.

### 5. Faculty Module
- **Manage Coursework & Assignments**: Create department-specific assignments, upload reference documents, and view submissions.
- **Submissions Grading**: Download student submissions, assign grades, and write custom evaluation feedback.
- **Attendance Marking by Roll Number**: Quick single Roll Number entry, batch Present/Absent toggles, and live search.
- **Results Management**: Enter semester GPA scores and record progress remarks directly from a tabular cohort panel.
- **Classroom Alerts & Timetable Management**: Post room change notices and configure class schedule slots.
- **Faculty Profile & ID Card**: Edit profile photo, office location, contact phone, and address. Generate and print official 2-sided **Faculty ID Card** with barcode (`FAC-100X`).

### 6. Student Module
- **Personalized Student Dashboard**: View profile photo, attendance statistics, current GPA standing, semester fee status, exam eligibility warnings, **Live Classroom Alerts**, and **Today's Class Schedule**.
- **Classroom Alerts & Notices**: Stay updated with live room relocations, lecture cancellations, and urgent notices.
- **Weekly Class Timetable**: View interactive weekly schedule with lecture timings, rooms, and assigned faculty.
- **My Assignments**: View outstanding coursework, submit files (PDF, Word, zip, etc.), and view grades/feedback.
- **Detailed Semester Results**: Access grade card dashboard, download/print grades, and view exam eligibility notices.
- **Two-Sided Student ID Card**: View and print official 2-sided **Student ID Card** with barcode (`STU-100X`), branch name, valid dates, and residential address.

---

## 🎴 Two-Sided Official ID Cards (Student, Faculty & Admin)

The system generates official printable identification cards for all user roles:

| Section | Included Information |
| :--- | :--- |
| **Header Banner** | `SMART COLLEGE` Logo + Role Badge (`STUDENT`, `FACULTY`, `ADMIN`) |
| **Title Banner** | Role Header (`STUDENT ID CARD`, `FACULTY ID CARD`, `ADMIN ID CARD`) |
| **Front Side** | Profile Photo, Full Name, Roll No / Employee ID / Admin ID, Branch Name / Department, Valid Date (`July 2026 - July 2028/2030`) |
| **Back Side** | Official Barcode SVG (generated via `JsBarcode`), Residential / Official Address, Phone, Email, Authorized Signatory Seal |

---

## 🛠️ Technical Stack & Architecture

- **Backend Framework**: Django 5.x (Python)
- **Frontend Layer**: HTML5, Vanilla CSS (Glassmorphic design system with Dark/Light themes), Bootstrap 5, FontAwesome 6, Chart.js, JsBarcode
- **Database Architecture**: Multi-database routing using **SQLite**:
  - `admin_db.sqlite3` (`accounts` app / Custom User profiles)
  - `students_db.sqlite3` (`students` app / Student profiles, assignments, submissions)
  - `faculty_db.sqlite3` (`faculty` app / Faculty profiles)
  - `db.sqlite3` (Default database / `departments`, `ClassroomAlert`, `TimetableSlot`, sessions)

---

## 🚀 Quick Setup & Installation

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Set Up Virtual Environment
```bash
# Create environment
python -m venv venv

# Activate on Windows PowerShell
venv\Scripts\Activate.ps1

# Activate on Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root directory:
```env
DEBUG=True
SECRET_KEY=django-insecure-smart-college-erp-development-key-12345
DATABASE_URL=sqlite:///db.sqlite3
STUDENTS_DATABASE_URL=sqlite:///students_db.sqlite3
FACULTY_DATABASE_URL=sqlite:///faculty_db.sqlite3
ADMIN_DATABASE_URL=sqlite:///admin_db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Apply Migrations Across Databases
```bash
python manage.py makemigrations
python manage.py migrate --database=default
python manage.py migrate --database=admin
python manage.py migrate --database=students
python manage.py migrate --database=faculty
```

### 6. Seed Initial Data
Populate pre-configured departments, faculty profiles, student records, classroom alerts, and timetable slots:
```bash
python seed_db.py
```

### 7. Run Server
```bash
python manage.py runserver 0.0.0.0:8000
```
Open **http://127.0.0.1:8000/** in your browser.

---

## 🔑 Demo Login Credentials

You can use the one-click magic auto-fill pill on the login page or enter credentials manually:

| Role | Username | Password | Access Rights |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin` | `admin123` | Full System Management & Admin ID Card |
| **Faculty (CSE)** | `prof_sharma` | `password123` | Coursework, Attendance by Roll No, Classroom Alerts, Timetable, Grading |
| **Faculty (EE)** | `prof_patel` | `password123` | Coursework, Attendance by Roll No, Classroom Alerts, Timetable, Grading |
| **Student (CSE)** | `student_amit` | `password123` | Assignments, GPA Results, Live Classroom Alerts, Today's Timetable, Student ID Card |
| **Student (EE)** | `student_sneha` | `password123` | Assignments, GPA Results, Live Classroom Alerts, Today's Timetable, Student ID Card |
| **Student (ME)** | `student_kabir` | `password123` | Assignments, GPA Results, Live Classroom Alerts, Today's Timetable, Student ID Card |
