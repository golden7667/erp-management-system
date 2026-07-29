# ⚡ Smart College ERP Management System

<p align="center">
  <img src="https://img.shields.io/badge/Django-5.x-092E20?style=for-the-badge&logo=django&logoColor=white" alt="Django" />
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white" alt="Bootstrap" />
  <img src="https://img.shields.io/badge/SQLite3-Multi--DB-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/REST%20API-JWT-FF6C37?style=for-the-badge&logo=postman&logoColor=white" alt="REST API" />
  <img src="https://img.shields.io/badge/UI/UX-Glassmorphism-FF69B4?style=for-the-badge" alt="Glassmorphism" />
</p>

---

## 📌 Executive Overview

**Smart College ERP** is an enterprise-grade Enterprise Resource Planning system crafted for academic institutions. Built on **Django 5.x**, it delivers real-time campus administration, strict multi-database security isolation, interactive timetables, roll-number attendance, and digital printable ID cards with live barcode generation.

> [!NOTE]
> Designed with modern **Glassmorphic UI aesthetics** powered by Bootstrap 5.3, FontAwesome 6, and Chart.js for real-time analytics.

---

## 🏗️ Multi-Database Router Architecture

The system enforces strict data security and domain separation through a custom Django database router (`college_erp/router.py`) that seamlessly isolates operations across **4 dedicated SQLite database engines**:


### Database Routing Specification

| Database File | Django App | Router Target Key | Handled Models & Domains |
| :--- | :--- | :--- | :--- |
| 🛡️ `admin_db.sqlite3` | `accounts` | `admin` | Custom User authentication model (`User`), Role assignments (`ADMIN`, `FACULTY`, `STUDENT`) |
| 🎓 `students_db.sqlite3` | `students` | `students` | Student Profiles, Roll Numbers, Attendance, Assignments, Submissions, GPA Results |
| 👨‍🏫 `faculty_db.sqlite3` | `faculty` | `faculty` | Faculty Profiles, Employee IDs, Designations, Qualifications, Subject Assignments |
| 🏛️ `db.sqlite3` | `departments` / Core | `default` | Departments, `ClassroomAlert`, `TimetableSlot`, Academic Sessions, Django System Tables |

---

## ⚡ Key Modules & Feature Highlights

### 📋 1. Sequential Roll-Number Attendance
* **Sorted Cohorts**: Students are automatically grouped and sorted by alphanumeric Roll Number (e.g., `CS-2026-101`).
* **Live Search**: Instant auto-complete search bar to pinpoint specific students.
* **One-Click Batch Actions**: Fast `Mark All Present` and `Mark All Absent` batch controls for faculty.

### 📢 2. Live Classroom Alerts & Notices
* **Real-time Broadcasts**: Emergency announcements, room changes, and exam schedules.
* **Priority Badging**: Clear badge tagging for `URGENT`, `HIGH`, `MEDIUM`, and `LOW` alerts.
* **Interactive Client Filtering**: Search by notice title, department, or priority level without page reloads.

### 🗓️ 3. Visual Weekly Timetable Grid
* **Weekly Matrix**: Interactive Monday-Saturday grid mapping hours, subjects, faculty, and room numbers.
* **Timeline Dashboard Card**: Dynamic **Today's Schedule** widget displaying ongoing and upcoming classes.

### 🎴 4. Two-Sided Digital Printable ID Cards
* **Role-Specific Designs**: Distinct layouts for **Students**, **Faculty**, and **Admins**.
* **Front Side**: Profile photo, Full Name, ID/Roll Number, Department, Role, and Validity Period.
* **Back Side**: Live **JsBarcode** SVG generation, emergency contact info, address, and official digital seal.

### 🖼️ 5. Dynamic Media & SVG Avatar Fallback System
* **Zero Broken Media**: Integrated custom media serve handler (`college_erp/urls.py`).
* **Automatic Fallbacks**: Missing user photos are automatically replaced with a clean dynamic SVG avatar without breaking UI layouts.

---

## 👑 Role-Based Capability Matrix

| Feature / Module | 👑 Admin | 👨‍🏫 Faculty | 🎓 Student |
| :--- | :---: | :---: | :---: |
| **System Analytics & User Creation** | ✅ | ❌ | ❌ |
| **Department & Alert Creation** | ✅ | ✅ | ❌ |
| **Take Attendance by Roll Number** | ✅ | ✅ | ❌ |
| **Manage & Grade Assignments** | ❌ | ✅ | ❌ |
| **View Today's Class Schedule** | ✅ | ✅ | ✅ |
| **View GPA Results & Submissions** | ❌ | ❌ | ✅ |
| **Printable Digital ID Card** | ✅ | ✅ | ✅ |

---

## 📂 Project Directory Structure

```text
erpsystem/
├── accounts/               # User Authentication, Password Reset & Role Routing
├── api/                    # Vercel Serverless Function & REST API Endpoints
│   └── index.py            # Vercel WSGI entrypoint
├── college_erp/            # Core Settings & Infrastructure
│   ├── router.py           # Custom Multi-Database Isolation Router
│   ├── settings.py         # Multi-DB config, WhiteNoise, Vercel /tmp setup
│   ├── urls.py             # Global URL patterns & SVG media fallback handler
│   └── wsgi.py             # WSGI application interface
├── departments/            # Departments, Classroom Alerts & Timetable Grids
├── faculty/                # Faculty Directory, Subject Allocation & Grading
├── media/                  # User Uploaded Photos & Media Assets
├── static/                 # CSS Stylesheets, JS Scripts, Logos & Static Assets
├── staticfiles/            # Production collected static assets
├── students/               # Student Profiles, Roll Attendance & Submissions
├── templates/              # Glassmorphic HTML5 Templates
│   ├── dashboard/          # Role-specific Dashboards (Admin, Faculty, Student)
│   ├── departments/        # Alerts & Timetable Templates
│   ├── faculty/            # Grading & Assignment Templates
│   ├── registration/       # Role-specific Login & Password Reset Templates
│   └── students/           # ID Cards, Results & Submissions Templates
├── admin_db.sqlite3        # Admin & User Authentication Database
├── db.sqlite3              # Core Department & System Database
├── faculty_db.sqlite3      # Faculty Database
├── students_db.sqlite3     # Student Database
├── manage.py               # Django Management CLI
├── seed_db.py              # Automated Multi-DB Seeding Script
├── vercel.json             # Vercel Serverless Routing Config
└── requirements.txt        # Python Dependencies Specification
```

---

## 🚀 Quick Setup & Installation Guide

### Step 1: Clone Repository & Create Virtual Environment

 
# On Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# On macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies & Environment Configuration

```bash
pip install -r requirements.txt
```

Create a `.env` file in the root directory:

```env
DEBUG=True
SECRET_KEY=django-insecure-smart-college-erp-dev-key
DATABASE_URL=sqlite:///db.sqlite3
STUDENTS_DATABASE_URL=sqlite:///students_db.sqlite3
FACULTY_DATABASE_URL=sqlite:///faculty_db.sqlite3
ADMIN_DATABASE_URL=sqlite:///admin_db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1,.vercel.app
```

### Step 3: Execute Multi-Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate --database=default
python manage.py migrate --database=admin
python manage.py migrate --database=students
python manage.py migrate --database=faculty
```

### Step 4: Seed Demo Data & Launch Server

```bash
python seed_db.py
python manage.py runserver
```

> [!TIP]
> Access the live ERP system in your web browser at **`http://127.0.0.1:8000/`**.

---

## 🔑 Pre-Configured Demo Test Accounts

| Role | Username | Password | Email | Scope & Description |
| :--- | :--- | :--- | :--- | :--- |
| **👑 Admin** | `admin` | `admin123` | `admin@smart.erp` | Superuser: System management & analytics |
| **👨‍🏫 Faculty** | `prof_sharma` | `password123` | `sharma@smart.erp` | Computer Science & Engineering Faculty |
| **👨‍🏫 Faculty** | `prof_patel` | `password123` | `patel@smart.erp` | Electrical Engineering Faculty |
| **🎓 Student** | `student_amit` | `password123` | `amit@smart.erp` | CSE Student (Roll: `CS-2026-992`) |
| **🎓 Student** | `student_sneha` | `password123` | `sneha@smart.erp` | EE Student (Roll: `EE-2026-102`) |
| **🎓 Student** | `student_kabir` | `password123` | `kabir@smart.erp` | ME Student (Roll: `ME-2026-054`) |

---

## 🔑 REST API & Authentication Endpoints

The project includes built-in REST API endpoints with **JWT (JSON Web Tokens)** support:

```text
POST /accounts/api/token/              # Obtain JWT access and refresh token pair
POST /accounts/api/token/refresh/      # Refresh JWT access token
GET  /students/api/students/           # JSON list of student profiles & GPA
GET  /faculty/api/faculty/             # JSON list of faculty directory
GET  /departments/api/alerts/          # JSON list of active classroom alerts
```

 
---

## 📄 License & Attribution

Designed & developed for **Smart College ERP Management System**. All rights reserved.
