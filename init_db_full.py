import mysql.connector
from mysql.connector import Error
import os

from dotenv import load_dotenv
import os
load_dotenv()

def get_connection(db=None):
    """Get MySQL connection (db=None for no specific DB)"""
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'SriVishnu@143'),
        database=db
    )

print("Academic Management System - FULL DB SETUP")
print("Database: bima")

# 1. CREATE DATABASE
try:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS bima")
    conn.close()
    print("Database 'bima' created/verified")
except Error as e:
    print(f"DB Error: {e}")

# 2. RUN FULL SCHEMA
config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'), 
    'password': os.getenv('DB_PASSWORD', 'SriVishnu@143'),
    'database': os.getenv('DB_NAME', 'bima')
}

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    # Basic tables (admin, students, teachers - extend existing)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE,
        password VARCHAR(100)
    )""")
    
    # Students (existing + FKs)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id VARCHAR(20) UNIQUE NOT NULL,
        name VARCHAR(100) NOT NULL,
        password VARCHAR(100),
        gender VARCHAR(10),
        dob DATE,
        branch VARCHAR(50),
        semester INT,
        branch_id INT,
        semester_id INT,
        mobile VARCHAR(15),
        father_mobile VARCHAR(15),
        photo VARCHAR(255),
        english INT DEFAULT 0, mathematics INT DEFAULT 0, physics INT DEFAULT 0,
        chemistry INT DEFAULT 0, computer_science INT DEFAULT 0,
        total INT DEFAULT 0, percentage DECIMAL(5,2) DEFAULT 0,
        FOREIGN KEY (branch_id) REFERENCES branches(id),
        FOREIGN KEY (semester_id) REFERENCES semesters(id)
    )""")
    
    cursor.execute("""\n    CREATE TABLE IF NOT EXISTS teachers (\n        id INT AUTO_INCREMENT PRIMARY KEY,\n        teacher_id VARCHAR(20) UNIQUE NOT NULL,\n        teacher_code VARCHAR(20) UNIQUE,\n        name VARCHAR(100) NOT NULL,\n        password VARCHAR(100),\n        gender VARCHAR(10),\n        dob DATE,\n        branch VARCHAR(50),\n        subjects TEXT,\n        phone VARCHAR(15),\n        photo VARCHAR(255),\n        email VARCHAR(100)\n    )""")
    
    # NEW NORMALIZED TABLES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS branches (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(50) UNIQUE NOT NULL
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS semesters (
        id INT AUTO_INCREMENT PRIMARY KEY,
        sem_no INT UNIQUE NOT NULL
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INT AUTO_INCREMENT PRIMARY KEY,
        subject_name VARCHAR(100) NOT NULL,
        branch_id INT,
        semester_id INT,
        FOREIGN KEY (branch_id) REFERENCES branches(id),
        FOREIGN KEY (semester_id) REFERENCES semesters(id)
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teacher_subjects (
        id INT AUTO_INCREMENT PRIMARY KEY,
        teacher_id VARCHAR(20),
        subject_id INT,
        FOREIGN KEY (subject_id) REFERENCES subjects(id),
        UNIQUE (teacher_id, subject_id)
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS marks (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id VARCHAR(20),
        subject_id INT,
        internal_exam_1 INT DEFAULT 0 CHECK (internal_exam_1 >= 0 AND internal_exam_1 <= 40),
        internal_exam_2 INT DEFAULT 0 CHECK (internal_exam_2 >= 0 AND internal_exam_2 <= 40),
        internal_exam_3 INT DEFAULT 0 CHECK (internal_exam_3 >= 0 AND internal_exam_3 <= 40),
        total_marks INT GENERATED ALWAYS AS (internal_exam_1 + internal_exam_2 + internal_exam_3) STORED,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(id),
        UNIQUE KEY unique_student_subject (student_id, subject_id)
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS announcements (
        id INT AUTO_INCREMENT PRIMARY KEY,
        message TEXT,
        target_audience VARCHAR(50) DEFAULT 'all',
        created_by VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    
    conn.commit()
    print("All tables created/verified")
    
except Error as e:
    print(f"Schema Error: {e}")
finally:
    if conn.is_connected():
        cursor.close()
        conn.close()

# 3. POPULATE DATA
try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    # Default admin
    cursor.execute("INSERT IGNORE INTO admin (username, password) VALUES ('admin', 'admin123')")
    
    # Branches
    branches = [('MCA',), ('MBA',)]
    for b in branches:
        cursor.execute("INSERT IGNORE INTO branches (name) VALUES (%s)", b)
    
    # Semesters 1-4
    for sem in range(1,5):
        cursor.execute("INSERT IGNORE INTO semesters (sem_no) VALUES (%s)", (sem,))
    
    # Subjects (from subjects_data.js - DYNAMIC!)
    subjects = [
        # MCA
        ('Programming', 1, 1), ('Mathematics', 1, 1), ('Computer Fundamentals', 1, 1), 
        ('Digital Logic', 1, 1), ('C Programming', 1, 1), ('Statistics', 1, 1),
        ('Data Structures', 1, 2), ('DBMS', 1, 2), ('Operating Systems', 1, 2),
        ('Java', 1, 2), ('Software Engineering', 1, 2), ('Computer Organization', 1, 2),
        ('Machine Learning', 1, 3), ('Computer Networks', 1, 3), ('Web Technology', 1, 3),
        ('Python', 1, 3), ('Data Mining', 1, 3), ('AI', 1, 3), ('Mini Project', 1, 3),
        ('Main Project', 1, 4),
        # MBA  
        ('Management Principles', 2, 1), ('Accounting', 2, 1), ('Economics', 2, 1),
        ('Business Law', 2, 1), ('Organizational Behavior', 2, 1), ('Statistics', 2, 1),
        ('Marketing', 2, 2), ('Finance', 2, 2), ('HR', 2, 2), ('Operations', 2, 2),
        ('MIS', 2, 2), ('Research Methods', 2, 2)
    ]
    for subj in subjects:
        cursor.execute("""
        INSERT IGNORE INTO subjects (subject_name, branch_id, semester_id) 
        VALUES (%s, %s, %s)
        """, subj)
    
    # Sample students (update FKs)
    cursor.execute("INSERT IGNORE INTO students (student_id, name, password, branch, semester, mobile, branch_id, semester_id) VALUES "
                  "('MCA001', 'Alice Johnson', 'pass123', 'MCA', 1, '9876543210', 1, 1), "
                  "('MCA002', 'Bob Smith', 'pass123', 'MCA', 2, '9876543211', 1, 2), "
                  "('MBA001', 'Carol Lee', 'pass123', 'MBA', 1, '9876543212', 2, 1)")
    
    # Sample teachers + assignments
    cursor.execute("INSERT IGNORE INTO teachers (teacher_id, name, password, branch, subjects, phone) VALUES "
                  "('T001', 'Dr. Jane Doe', 'teach123', 'MCA', 'Math,Physics,Data Structures', '9876543213')")
    
    cursor.execute("""
    INSERT IGNORE INTO teacher_subjects (teacher_id, subject_id)
    SELECT 'T001', id FROM subjects WHERE subject_name IN ('Mathematics','Data Structures','Programming')
    """)
    
    # Sample marks
    cursor.execute("""
    INSERT IGNORE INTO marks (student_id, subject_id, internal_exam_1, internal_exam_2, internal_exam_3) VALUES
    ('MCA001', (SELECT id FROM subjects WHERE subject_name='Mathematics' AND branch_id=1), 22, 24, 23),
    ('MCA001', (SELECT id FROM subjects WHERE subject_name='Programming' AND branch_id=1), 20, 22, 21),
    ('MCA002', (SELECT id FROM subjects WHERE subject_name='Data Structures' AND branch_id=1), 18, 19, 20)
    ON DUPLICATE KEY UPDATE internal_exam_1=VALUES(internal_exam_1), internal_exam_2=VALUES(internal_exam_2), internal_exam_3=VALUES(internal_exam_3)
    """)
    
    conn.commit()
    cursor.execute("SELECT COUNT(*) as subjects FROM subjects")
    subj_count = cursor.fetchone()[0]
    print(f"✅ Data populated: {subj_count} subjects, sample students/teachers/marks")
    
except Error as e:
    print(f"❌ Data Error: {e}")
finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()

print("\n🎉 FULL DB READY! Run: python app.py")
print("Test logins: admin/admin123 | T001/teach123 | MCA001/pass123")

