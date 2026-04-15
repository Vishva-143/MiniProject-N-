# Academic Performance Analytics System

A **full-stack web application** built using **Flask + MySQL + JavaScript** to manage, analyze, and visualize student academic performance dynamically.

---

## Overview

The **Academic Performance Analytics System** is designed to streamline academic management for **Admins, Teachers, and Students**. It provides:

- Real-time performance analytics  
- Dynamic subject allocation (branch + semester)  
- Rule-based insights on the **AI Assistant** page  
- Interactive dashboards (Chart.js on the admin dashboard)  

---

## Key Features

### Admin Panel

- Dashboard with analytics (total students, marks average, topper)  
- Manage students (register, quick add with marks, table view, edit, delete, PDF)  
- Manage teachers (register, edit, delete, PDF)  
- Dynamic subject selection for teachers via `/get_subjects/<branch>/<semester>`  
- Announcements (with optional file upload)  
- Analytics and AI Assistant pages  

### Teacher Panel

- Profile and assigned subjects  
- Enter marks (`/add_marks`; admins can use `?as_teacher=<teacher_id>`)  
- Students listed by branch; marks per subject  
- View announcements and assistant  

### Student Panel

- Profile and semester-wise marks (`/student/<id>`)  
- Percentage and grade calculation in the UI  
- Announcements  

---

## Dynamic Subject System

Subjects are resolved from MySQL using **branch** and **semester** (normalized `branches`, `semesters`, and `subjects` tables).

### Workflow

1. Student registers (or quick add) → rows in `students`  
2. **`student_subjects`** is populated automatically for that student’s branch + semester (all matching subjects)  
3. Teachers pick subjects per **branch + semester** at registration  
4. Marks are stored per `student_id` + `subject_id`  

---

## Project structure

```
Mini-Project/
├── app.py
├── requirements.txt
├── .env.example
├── schema_academic.sql          # optional extended schema helpers
├── init_db_full.py              # optional full DB bootstrap
├── static/
│   ├── Style.css
│   ├── subjects_data.js
│   ├── favicon.svg
│   └── uploads/
└── templates/
    ├── base.html
    ├── login.html
    ├── admin_dashboard.html
    ├── admin_navbar.html
    ├── teacher_dashboard.html
    ├── teacher_navbar.html
    ├── teacher_details.html
    ├── student_dashboard.html
    ├── student_navbar.html
    ├── students.html
    ├── teachers.html
    ├── register_student.html
    ├── register_student_original.html
    ├── register_teacher.html
    ├── add_student.html
    ├── add_marks.html
    ├── update_student.html
    ├── update_teacher.html
    ├── student_details.html
    ├── view_students.html
    ├── analytics.html
    ├── announcements.html
    ├── edit_announcement.html
    ├── assistant.html
    ├── forgot_password.html
    ├── otp_verify.html
    ├── reset_password.html
    ├── teacher_forgot_password.html
    ├── teacher_verify_otp.html
    └── teacher_reset_password.html
```

All of the above templates are wired to routes in `app.py` (including auth, password reset, and alternate student registration).

---

## Database design (MySQL)

The running app uses a **normalized** schema (see `init_db_full.py` / `schema_academic.sql`): `branches`, `semesters`, `subjects` with `branch_id` / `semester_id`, and `subject_name` as the subject title (equivalent to the conceptual `name` below).

### Logical tables (as in your spec)

**Students** — stored with extra fields for passwords, marks columns, FKs, etc.

**Teachers** — extended with email, photo, `teacher_subjects` mapping.

**Mapping**

- `teacher_subjects (teacher_id, subject_id)`  
- **`student_subjects (student_id, subject_id)`** — auto-filled on student create  

**Marks**

```sql
marks (
  student_id VARCHAR(20),
  subject_id INT,
  internal_exam_1 INT,
  internal_exam_2 INT,
  internal_exam_3 INT
);
```

`ensure_schema()` in `app.py` creates `student_subjects` if it is missing.

---

## API routes

| Route | Description |
|--------|-------------|
| `GET /get_subjects/<branch>/<semester>` | Subjects for branch (MCA/MBA) and semester (1–4 or “Semester 1”) |
| `GET /get_subjects/<branch>` | All subjects for that branch (all semesters) |
| `GET /teacher_subjects/<teacher_id>` | JSON list of teacher’s subjects |
| `GET /get_students_for_subject/<subject_id>` | Students in same branch + semester as subject |
| `GET /get_marks/<student_id>?semester_id=` | Marks JSON for UI |
| `POST /update_marks` | JSON body: student_id, subject_id, marks |
| `GET/POST /add_marks` | Page (GET) or save marks JSON (POST) |

---

## Analytics & UI

- **Chart.js** on `admin_dashboard.html` (student percentages + class summary).  
- Dark / glass-style layout via `static/Style.css` and Bootstrap 5.  

### Assistant (“AI”) behaviour

The **Assistant** page answers from live SQL (topper, class average, weak students). Thresholds for teacher dashboard suggestions: weak &lt; 50%, average &lt; 75%, else excellent.

### Grade hints (UI)

Student detail views compute letter grades from percentage; you can align display rules with your institution.

---

## Installation

### 1. Clone and enter the project

```bash
git clone <your-repo-url>
cd Mini-Project
```

### 2. Dependencies

```bash
pip install -r requirements.txt
```

### 3. MySQL

Create a database (default name **`bima`** unless overridden). You can use:

```bash
python init_db_full.py
```

(or run your own SQL) so `branches`, `semesters`, `subjects`, `students`, `teachers`, `marks`, etc. exist.

### 4. Configure environment

Copy `.env.example` to `.env` and set:

- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_PORT`  
- `SECRET_KEY`  

### 5. Password hashing

If logins fail after seeding plain-text passwords, run:

```bash
python fix_passwords.py
```

### 6. Run

```bash
python app.py
```

Open **http://127.0.0.1:5000/**  

Default admin shortcut in code: username **`admin`**, password **`admin`** (also supports `admin` / `admin123` style rows from DB when hashed or plain).

---

## Usage flow

- **Admin** — Login → dashboard → manage teachers/students → analytics / assistant.  
- **Teacher** — Login → dashboard → **Enter marks** → announcements.  
- **Student** — Login → dashboard → profile/marks → announcements.  

---

## Future enhancements

- Attendance module  
- Email / SMS notifications  
- Predictive models  
- Cloud deploy (Render, AWS, etc.)  
- Mobile client  

---

## Tech stack

- **Backend:** Flask (Python)  
- **Database:** MySQL  
- **Frontend:** HTML, CSS, JavaScript  
- **Charts:** Chart.js  
- **PDF:** ReportLab (student/teacher reports)  

---

## Author

**Vishnu** — Full-stack developer passionate about building intelligent academic systems.

---

## License

Educational use only.

---

## Support

If you like this project, star the repo, fork it, and share it.
