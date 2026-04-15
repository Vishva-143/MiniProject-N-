# 📚 Academic Performance Analytics System (BIMA)

A **comprehensive full-stack web application** for managing student academic performance, marks tracking, and institutional analytics with real-time dashboards, exam-wise summaries, and multi-role access control.

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Technology Stack](#technology-stack)
3. [Key Features](#key-features)
4. [Project Structure](#project-structure)
5. [Database Design](#database-design)
6. [Installation & Setup](#installation--setup)
7. [Usage Guide](#usage-guide)
8. [API Routes](#api-routes)
9. [Recent Enhancements](#recent-enhancements)
10. [Configuration](#configuration)
11. [Future Enhancements](#future-enhancements)

---

## 🎯 Overview

**BIMA** (Academic Performance Analytics System) is a role-based academic management platform designed for educational institutions to:
- Manage student enrollments across multiple programs and semesters
- Track subject-wise marks with exam breakdown (Exam 1, Exam 2, Exam 3)
- Generate real-time analytics and performance dashboards
- Enable teachers to input and manage marks efficiently
- Provide students with comprehensive performance tracking and self-service profile management
- Support institutional decision-making with analytics and insights

**User Roles:** Admin, Teacher, Student

**Supported Programs:** MCA, MBA (extensible)

**Supported Semesters:** Semester 1-4 (configurable)

---

## 🛠️ Technology Stack

### **Backend**
| Technology | Purpose | Version |
|-----------|---------|---------|
| **Python** | Backend language | 3.8+ |
| **Flask** | Web framework | 2.x |
| **MySQL/MariaDB** | Primary database | 5.7+ |
| **mysql-connector-python** | MySQL driver | Latest |
| **bcrypt** | Password hashing | Latest |
| **python-dotenv** | Environment configuration | Latest |
| **ReportLab** | PDF generation | Latest |
| **Werkzeug** | File upload handling | Latest |

### **Frontend**
| Technology | Purpose |
|-----------|---------|
| **HTML5** | Markup structure |
| **CSS3** | Styling and layouts |
| **Bootstrap 5** | Responsive UI components |
| **JavaScript (Vanilla)** | Client-side interactions |
| **Chart.js** | Data visualization & analytics |
| **jQuery (optional)** | DOM manipulation |
| **Font Awesome 6** | Icons library |

### **Database**
| Component | Details |
|-----------|---------|
| **Database Engine** | MySQL 5.7+ / MariaDB |
| **Tables** | Students, Teachers, Marks, Subjects, Branches, Semesters, Announcements |
| **Relationships** | Normalized schema with foreign keys |
| **Normalization** | 3NF (Third Normal Form) |

### **Security**
- **Password Hashing:** bcrypt with salt
- **Session Management:** Flask session with SECRET_KEY
- **Role-Based Access Control:** Admin, Teacher, Student roles
- **CSRF Protection:** Integrated with Flask
- **Authentication:** Session-based with login/logout

### **Deployment & DevOps**
- **Server:** Flask development server (production-ready with WSGI)
- **Environment:** Windows/Linux/Mac compatible
- **Version Control:** Git
- **Package Manager:** pip

---

## ✨ Key Features

### 🔐 **Admin Panel** (Full Access)

#### Dashboard & Analytics
- **Analytics Dashboard:** Real-time metrics with visualizations
  - Total students, teachers, subjects
  - Class average percentage
  - Top performer identification
  - Grade distribution charts
- **Exam-wise Analytics:** Separate tracking for Exam 1, 2, and 3
  - Total marks per exam across all subjects
  - Percentage calculations per exam
  - Grade distribution per exam
  - Subject-wise exam performance

#### Student Management
- **Register Students:** Bulk add with branch and semester selection
- **Quick Add:** Add marks during student creation
- **View Students:** Tabular view with search/filter
- **Edit Students:** Update all profile details
- **Delete Students:** Remove with data cleanup
- **Download PDF:** Generate student report cards
- **Profile Editing:** Students can now update their own details
  - Name, Email, DOB, Mobile numbers
  - Password management
  - Photo upload

#### Teacher Management
- **Register Teachers:** Assign subjects per branch/semester
- **View Teachers:** List all teachers with details
- **Edit Teachers:** Modifiable subject assignments
- **Delete Teachers:** Remove with cascade cleanup
- **Download PDF:** Export teacher information

#### Marks Management
- **Add Marks:** Per student per subject per exam
- **Track 3 Exams:** Separate columns for Exam 1, 2, 3
- **Calculate Totals:** Automatic exam-wise and overall totals
- **Percentage Calculation:** Based on actual subject count (not fixed)
- **Grade Assignment:** Automatic grade calculation

#### Announcements System
- **Create Announcements:** Post important messages
- **File Uploads:** Attach documents/images
- **Edit/Delete:** Manage existing announcements
- **Visibility Control:** Show to all roles or specific roles

#### Dynamic Subject Allocation
- **Branch-wise Subjects:** Different subjects per program (MCA/MBA)
- **Semester-wise Subjects:** Semester-specific curriculum
- **Auto-assignment:** Student subjects auto-updated on registration
- **API Integration:** `/get_subjects/<branch>/<semester>`

### 📊 **Teacher Dashboard** (Subject Assignment)

#### Dashboard & Analytics
- **Teacher Analytics:** Personal metrics
  - Total assigned subjects
  - Total students taught
  - Class average, topper, weak students
  - Exam-wise performance summaries

#### Marks Entry
- **Mark Sheet:** Streamlined interface for mark entry
  - Student list grouped by branch
  - Subject-wise mark input
  - Real-time validation
  - Batch save functionality

#### Student Tracking
- **View Students:** Per subject with attendance
- **Performance Analysis:** Subject-specific analytics
- **Weak Student Alerts:** Automatic identification
- **Suggestions:** AI Assistant provides insights

#### Communication
- **View Announcements:** Read admin/teacher announcements
- **AI Assistant:** Rule-based insights for teaching

### 👨‍🎓 **Student Dashboard** (Self-Service)

#### Profile Management
- **View Profile:** Complete profile display
  - ID, Name, Branch, Semester
  - Enrollment dates, contact info
  - Photo display
- **Edit Profile:** NEW - Self-service profile updates
  - Name, Email, DOB
  - Mobile and father's mobile numbers
  - Password change with confirmation
  - Profile photo upload/update
  - Form validation with user feedback

#### Performance Tracking
- **Dashboard:** Profile + basic info
- **My Performance:** Detailed marks view with:
  - **Current Semester Marks**
    - All subjects with marks
    - Exam 1, 2, 3 breakdown
    - Subject totals (/120)
    - Subject percentages
    - Subject grades
  - **Previous Semester Marks:** Historical performance
    - Semester selector dropdown
    - All previous semesters available
    - Same detailed breakdown as current
  - **Exam-wise Summaries**
    - Exam 1 Total, Percentage, Grade
    - Exam 2 Total, Percentage, Grade
    - Exam 3 Total, Percentage, Grade
    - Overall Total, Percentage, Grade
  - **Grade Calculation:** A (90+), B (75-89), C (60-74), D (50-59), F (<50)

#### Announcements
- **Read Announcements:** View institutional announcements
- **Download Attachments:** Access announcement files

#### Enhanced Security
- **Login Page:** Password visibility toggle with eye icon
  - Show/hide password functionality
  - Smooth UX on login

### 🤖 **AI Assistant** (All Roles)

- **Rule-based Insights:** SQL-driven suggestions
- **Weak Student Alerts:** Performance monitoring
- **Class Statistics:** Real-time analytics
- **Teacher Actionability:** Suggests interventions

---

## 📁 Project Structure

```
Mini-Project/
│
├── app.py                                    # Main Flask application
├── requirements.txt                          # Python dependencies
├── .env.example                             # Environment variables template
├── README.md                                # Documentation
├── TODO.md                                  # Development tasks
│
├── Database Setup Scripts/
│   ├── init_db.py                          # Basic database initialization
│   ├── init_db_full.py                     # Full database setup
│   ├── schema_academic.sql                 # SQL schema definition
│   ├── preload_data.sql                    # Sample data insertion
│   ├── setup_full_project.py               # Complete project setup
│   ├── run_schema.py                       # Schema execution
│   ├── fix_passwords.py                    # Password hashing utility
│   ├── fix_teachers_schema.py              # Teacher schema fixes
│   ├── migrate_marks.py                    # Marks migration script
│   ├── migrate_marks_fixed.py              # Fixed marks migration
│   ├── load_subjects.py                    # Subject loader
│   ├── update_subjects.py                  # Subject updater
│   └── test_subjects.py                    # Subject testing
│
├── static/                                   # Static assets
│   ├── Style.css                           # Custom styling
│   ├── subjects_data.js                    # Subject JSON data
│   └── uploads/                            # File uploads directory
│       └── teachers/                       # Teacher photos
│
└── templates/                                # HTML templates
    ├── base.html                           # Base template (extends)
    │
    ├── Authentication/
    │   ├── login.html                      # Multi-role login page
    │   ├── forgot_password.html            # Forgot password
    │   ├── reset_password.html             # Password reset form
    │   ├── otp_verify.html                 # OTP verification
    │   ├── teacher_forgot_password.html    # Teacher password recovery
    │   ├── teacher_reset_password.html     # Teacher password reset
    │   └── teacher_verify_otp.html         # Teacher OTP page
    │
    ├── Admin/
    │   ├── admin_dashboard.html            # Admin home with analytics
    │   ├── admin_navbar.html               # Admin navigation
    │   ├── students.html                   # Student management list
    │   ├── add_student.html                # Quick add student
    │   ├── update_student.html             # Edit student
    │   ├── register_student.html           # Student registration
    │   ├── teachers.html                   # Teacher management list
    │   ├── register_teacher.html           # Teacher registration
    │   ├── update_teacher.html             # Edit teacher
    │   ├── analytics.html                  # Analytics dashboard
    │   ├── announcements.html              # Manage announcements
    │   └── edit_announcement.html          # Edit announcement
    │
    ├── Teacher/
    │   ├── teacher_dashboard.html          # Teacher home
    │   ├── teacher_navbar.html             # Teacher navigation
    │   ├── add_marks.html                  # Mark entry page
    │   ├── teacher_details.html            # View teacher profile
    │   ├── student_details.html            # View student (from teacher)
    │   ├── view_students.html              # Student list for teacher
    │   ├── upgrade_semester.html           # Semester upgrade
    │   ├── upgrade_semester_search.html    # Semester search
    │   └── assistant.html                  # AI Assistant insights
    │
    └── Student/
        ├── student_dashboard.html          # Student profile page
        ├── student_navbar.html             # Student navigation
        ├── student_performance.html        # Marks and performance view
        ├── student_details.html            # Full profile with marks
        ├── student_edit_profile.html       # Profile edit form (NEW)
        └── assistant.html                  # AI Assistant (shared)
```

---

## 💾 Database Design

### **Normalized Schema (3NF)**

#### **Core Tables**

**`branches`**
```sql
- branch_id (PK)
- branch_name (VARCHAR) - e.g., "MCA", "MBA"
- description (TEXT)
```

**`semesters`**
```sql
- semester_id (PK)
- semester_no (INT) - 1, 2, 3, 4
- semester_name (VARCHAR) - e.g., "Semester 1"
```

**`subjects`**
```sql
- subject_id (PK)
- subject_name (VARCHAR)
- branch_id (FK) - MCA, MBA specific
- semester_id (FK) - Semester specific
- credits (INT)
```

**`students`**
```sql
- student_id (VARCHAR) - Unique ID (SBIMAMCA006)
- password (VARCHAR) - bcrypt hash
- name (VARCHAR)
- email (VARCHAR)
- dob (DATE)
- mobile (VARCHAR)
- father_mobile (VARCHAR)
- gender (ENUM)
- branch_id (FK) - MCA/MBA
- semester_id (FK) - Current semester
- photo (VARCHAR) - Filename/path
- created_at (DATETIME)
- updated_at (DATETIME)
```

**`teachers`**
```sql
- teacher_id (VARCHAR) - Unique ID (SBIT0001)
- password (VARCHAR) - bcrypt hash
- name (VARCHAR)
- email (VARCHAR)
- phone (VARCHAR)
- photo (VARCHAR)
- subject_specialization (VARCHAR)
- created_at (DATETIME)
- updated_at (DATETIME)
```

**`teacher_subjects`** (Many-to-Many)
```sql
- teacher_id (FK)
- subject_id (FK)
- assigned_date (DATETIME)
- PRIMARY KEY (teacher_id, subject_id)
```

**`student_subjects`** (Many-to-Many)
```sql
- student_id (FK)
- subject_id (FK)
- assigned_date (DATETIME)
- PRIMARY KEY (student_id, subject_id)
```

**`marks`**
```sql
- mark_id (PK)
- student_id (FK)
- subject_id (FK)
- exam1_marks (INT) - 0-40
- exam2_marks (INT) - 0-40  
- exam3_marks (INT) - 0-40
- total_marks (INT) - Auto calculated (sum of exams)
- percentage (DECIMAL)
- grade (VARCHAR)
- created_at (DATETIME)
- updated_at (DATETIME)
```

**`announcements`**
```sql
- announcement_id (PK)
- title (VARCHAR)
- content (TEXT)
- file_path (VARCHAR) - Optional attachment
- created_by (FK) - Teacher/Admin ID
- created_at (DATETIME)
- updated_at (DATETIME)
- is_active (BOOLEAN)
```

---

## 🚀 Installation & Setup

### **Prerequisites**
- Python 3.8 or higher
- MySQL 5.7 or MariaDB 10.3+
- pip (Python package manager)
- Git

### **Step 1: Clone the Repository**
```bash
git clone <your-repository-url>
cd Mini-Project
```

### **Step 2: Create Virtual Environment**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### **Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 4: Setup Database**

#### Option A: Automated Setup
```bash
python setup_full_project.py
```

#### Option B: Manual Setup
```bash
# Create MySQL database
mysql -u root -p < schema_academic.sql

# Load sample data (optional)
python init_db_full.py

# Load initial subjects
python load_subjects.py

# Hash passwords if using plain text
python fix_passwords.py
```

### **Step 5: Configure Environment**

Create `.env` file in project root:
```env
# Database Configuration
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=bima
DB_PORT=3306

# Flask Configuration
SECRET_KEY=your_secret_key_here_min_32_chars
FLASK_ENV=development
DEBUG=True

# Upload Settings
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=5242880  # 5MB
```

### **Step 6: Run Application**
```bash
python app.py
```

Access at: **http://127.0.0.1:5000/**

---

## 📖 Usage Guide

### **Admin Workflow**

1. **Login** → Admin role
2. **Dashboard** → View analytics (total students, average %, exam-wise metrics)
3. **Manage Students** → Register, edit, delete, download reports
4. **Manage Teachers** → Register with subject assignments
5. **Add Marks** → Manual entry or bulk assignment
6. **Analytics** → View detailed performance charts
7. **Announcements** → Create and manage institutional messages
8. **AI Assistant** → Get insights and recommendations

### **Teacher Workflow**

1. **Login** → Teacher role
2. **Dashboard** → View assigned subjects and student count
3. **Add Marks** → Enter marks for assigned students/subjects
4. **View Students** → See enrolled students
5. **Analytics** → Track class performance
6. **Announcements** → View institutional communications
7. **AI Assistant** → Get teaching suggestions (weak students, class average)

### **Student Workflow**

1. **Login** → Student role
2. **Dashboard** → View personal profile and details
3. **Edit Profile** → Update name, email, DOB, mobile, password, photo
4. **My Performance** → View semester-wise marks
   - Select different semesters from dropdown
   - View all subjects with marks
   - See exam-wise breakdown (Exam 1, 2, 3 totals, percentages, grades)
   - View overall performance metrics
5. **Announcements** → Read important announcements
6. **AI Assistant** → Get performance insights

### **Key Interactions**

#### **Mark Calculation Formula**
```
Total Subject Marks = Exam1 + Exam2 + Exam3 (Max = 120)
Subject Percentage = (Subject Total / 120) * 100
Overall Percentage = (Sum of all Subject Totals) / (Subject Count * 120) * 100
```

#### **Grade Assignment**
```
A: 90-100%
B: 75-89%
C: 60-74%
D: 50-59%
F: Below 50%
```

---

## 🔌 API Routes

### **Marks & Analytics**

| Route | Method | Purpose | Response |
|-------|--------|---------|----------|
| `/get_marks/<student_id>` | GET | Fetch student marks with exam-wise breakdown | JSON: marks array + summary (exam1/2/3 totals, percentage, grade) |
| `/student_performance` | GET | Student's mark view with semester selector | HTML: Performance page |
| `/get_subjects/<branch>/<semester>` | GET | Subjects for branch and semester | JSON: Subject list |
| `/get_subjects/<branch>` | GET | All subjects for branch (all semesters) | JSON: Subject list |
| `/teacher_subjects/<teacher_id>` | GET | Teacher's assigned subjects | JSON: Subject list |
| `/get_students_for_subject/<subject_id>` | GET | Students in subject's branch/semester | JSON: Student list |

### **Authentication**

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Login page |
| `/login` | POST | Process login |
| `/logout` | GET | Logout user |
| `/forgot_password` | GET/POST | Password recovery |
| `/reset_password/<token>` | GET/POST | Reset password |
| `/otp_verify` | GET/POST | OTP verification |

### **Admin Routes**

| Route | Method | Purpose |
|-------|--------|---------|
| `/admin_dashboard` | GET | Admin home with analytics |
| `/students` | GET | Student list |
| `/add_student` | GET/POST | Quick add student |
| `/update_student/<id>` | GET/POST | Edit student |
| `/teachers` | GET | Teacher list |
| `/register_teacher` | GET/POST | Register teacher |
| `/update_teacher/<id>` | GET/POST | Edit teacher |
| `/add_marks` | GET/POST | Mark entry |
| `/announcements` | GET/POST | Manage announcements |
| `/analytics` | GET | Analytics dashboard |

### **Teacher Routes**

| Route | Method | Purpose |
|-------|--------|---------|
| `/teacher_dashboard` | GET | Teacher home |
| `/teacher/<id>` | GET | Teacher profile |
| `/add_marks` | GET/POST | Enter marks |
| `/teacher/<id>/students` | GET | Students by teacher |

### **Student Routes**

| Route | Method | Purpose |
|-------|--------|---------|
| `/student_dashboard` | GET | Student profile |
| `/student_performance` | GET | Student marks view |
| `/edit_student_profile` | GET/POST | Edit profile (name, email, DOB, mobile, password, photo) |
| `/student/<id>` | GET | Full student details (admin/teacher view) |

---

## 🆕 Recent Enhancements

### **Phase: Student Profile Editing**
✅ **Feature:** Students can now update their own profile
- **Fields Editable:**
  - Full Name
  - Email Address
  - Date of Birth
  - Mobile Number (10 digits)
  - Father's Mobile Number (10 digits)
  - Password (with confirmation)
  - Profile Photo (JPG, PNG, GIF)

- **Security Features:**
  - Password hashed with bcrypt
  - File upload validation (image formats only)
  - Email format validation
  - Phone number validation
  - Form-level and server-side validation

- **User Experience:**
  - Pre-filled form with current data
  - Show/hide password toggle
  - Photo preview with current photo display
  - Success/error flash messages
  - Redirect to dashboard after successful update

### **Phase: Exam-Wise Mark Breakdowns**
✅ Implemented across all dashboards:
- Individual Exam 1, 2, 3 totals and percentages
- Subject-wise exam performance
- Exam-wise grade calculation
- Overall performance metrics
- Semester-wise historical tracking

### **Phase: Dashboard/Performance Separation**
✅ **Student Dashboard:**
- Profile display only (name, photo, contact info)
- "Edit Profile" button for self-service updates
- "View My Performance" button to navigate to marks

✅ **Student Performance:**
- Marks visualization
- Semester selector for historical data
- Full exam-wise breakdown
- Comprehensive performance metrics

### **Phase: Login Enhancements**
✅ Password visibility toggle:
- Eye icon to show/hide password
- Smooth UX transition
- Supported in both login and password reset forms

---

## ⚙️ Configuration

### **Environment Variables (.env)**
```env
# Database
DB_HOST=127.0.0.1
DB_USER=root
DB_PASSWORD=password
DB_NAME=bima
DB_PORT=3306

# Flask
SECRET_KEY=your_32_char_min_secret_key
FLASK_ENV=development
DEBUG=True

# File Upload
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=5242880  # 5MB
```

### **Customization Points**

#### **Add New Branch**
```sql
INSERT INTO branches (branch_name, description) 
VALUES ('B.Tech', 'Bachelor of Technology');
```

#### **Add New Subject**
```sql
INSERT INTO subjects (subject_name, branch_id, semester_id, credits)
VALUES ('Data Structures', 1, 1, 4);
```

#### **Adjust Grade Thresholds**
Edit in `app.py`:
```python
def calculate_grade(percentage):
    if percentage >= 90: return 'A'
    elif percentage >= 75: return 'B'
    # ... modify as needed
```

#### **Change Upload Path**
- Modify `UPLOAD_FOLDER` in `.env`
- Ensure directory has write permissions

---

## 🔐 Security Features

1. **Password Security**
   - Passwords hashed with bcrypt + salt
   - Salting prevents rainbow table attacks
   - Minimum 6-character requirements

2. **Session Management**
   - Secure cookies with SECRET_KEY
   - Session timeout support
   - Per-user role-based access

3. **File Upload Security**
   - Secure filename generation with `werkzeug.utils.secure_filename`
   - File type validation (JPG, PNG, GIF for photos)
   - File size limits (configurable)
   - Stored outside web root when possible

4. **SQL Injection Prevention**
   - Parameterized queries throughout
   - No raw string concatenation

5. **CSRF Protection**
   - Flask integrated CSRF tokens

---

## 📈 Performance Optimization

### **Database**
- Indexes on frequently queried columns (student_id, subject_id, teacher_id)
- Normalized schema reduces data duplication
- Efficient aggregation queries with GROUP BY and COUNT(DISTINCT)

### **Frontend**
- AJAX for dynamic mark loading
- CSS minification recommendations
- Lazy loading for images
- Chart.js for efficient visualization

### **Caching Considerations**
- Subject lists cached in JavaScript
- Consider Redis for session store in production

---

## 🔮 Future Enhancements

### **Short Term**
- [ ] Email notifications for announcements
- [ ] SMS alerts for low marks
- [ ] Attendance tracking module
- [ ] Discussion forum for students
- [ ] Assignment submission system

### **Medium Term**
- [ ] Mobile app (React Native/Flutter)
- [ ] Predictive analytics for at-risk students
- [ ] Export to Excel/CSV reports
- [ ] Scheduled report generation
- [ ] Parent portal access

### **Long Term**
- [ ] Machine learning for grade prediction
- [ ] Cloud deployment (AWS/Azure/Google Cloud)
- [ ] Multi-institution federation
- [ ] Blockchain certificates
- [ ] Integration with external educational APIs

### **DevOps**
- [ ] Docker containerization
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Kubernetes deployment
- [ ] Database backup automation
- [ ] Monitoring & logging (ELK stack)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📞 Support & Documentation

- **PDF Reports:** Admin and teacher can download reports
- **AI Assistant:** Built-in system for recommendations
- **Error Pages:** User-friendly error messages
- **Validation Feedback:** Form validation with helpful hints

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👨‍💼 Author & Contact

**Project:** Academic Performance Analytics System (BIMA)

**Last Updated:** April 2026

---

## 📊 Project Statistics

- **Lines of Code (Backend):** ~3000+ (Python/Flask)
- **HTML Templates:** 30+
- **Database Tables:** 8 core tables
- **User Roles:** 3 (Admin, Teacher, Student)
- **Supported Branches:** 2+ (MCA, MBA - extensible)
- **Supported Semesters:** 4 (1-4)
- **Key Features:** 40+
- **API Endpoints:** 30+

---

## 🎓 Learning Outcomes

This project demonstrates:
- Full-stack web development (Frontend + Backend + Database)
- Role-based access control implementation
- RESTful API design
- Database normalization and relationships
- Real-time data visualization
- File upload handling and security
- Password hashing and authentication
- PDF generation
- AJAX for dynamic content
- Bootstrap responsive design
- Git version control

---

**This README provides comprehensive documentation for the BIMA academic system. For specific technical questions, refer to inline code comments or the assistant feature.**
<<<<<<< HEAD
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
=======
# MiniProject-N-
>>>>>>> 7cd9113bdc32565128fd5d02f19bd36c3833bf84
