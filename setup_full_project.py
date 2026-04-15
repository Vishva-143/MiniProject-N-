#!/usr/bin/env python3
"""
Complete Project Setup and Initialization Script
Initializes database with all required tables, relationships, and sample data
"""

import mysql.connector
from mysql.connector import errors as mysql_errors
import bcrypt
import os
from datetime import datetime, timedelta

# Database configuration
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'SriVishnu@143',
    'port': 3306
}

def get_connection(db=None):
    """Get MySQL connection"""
    config = DB_CONFIG.copy()
    if db:
        config['database'] = db
    return mysql.connector.connect(**config)

def hash_password(password):
    """Hash password with bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def execute_sql(conn, sql, params=None):
    """Execute SQL and commit"""
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        conn.commit()
        return cursor
    except Exception as e:
        print(f"❌ Error executing SQL: {e}")
        conn.rollback()
        raise

def create_database():
    """Create main database"""
    print("\n🔧 Creating database...")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS bima")
        cursor.execute("USE bima")
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database 'bima' ready")
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        raise

def create_tables():
    """Create all required tables"""
    print("\n📋 Creating tables...")
    conn = get_connection('bima')
    cursor = conn.cursor()
    
    # Branches table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS branches (
            id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(50) UNIQUE NOT NULL
        )
    """)
    
    # Semesters table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS semesters (
            id INT PRIMARY KEY AUTO_INCREMENT,
            sem_no INT UNIQUE NOT NULL
        )
    """)
    
    # Admin table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL
        )
    """)
    
    # Students table with all required fields
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(20) UNIQUE NOT NULL,
            name VARCHAR(100),
            password VARCHAR(100),
            gender VARCHAR(10),
            dob DATE,
            branch VARCHAR(50),
            semester INT,
            branch_id INT,
            semester_id INT,
            specialization VARCHAR(50),
            mobile VARCHAR(15),
            father_mobile VARCHAR(15),
            photo VARCHAR(255),
            english INT DEFAULT 0,
            mathematics INT DEFAULT 0,
            physics INT DEFAULT 0,
            chemistry INT DEFAULT 0,
            computer_science INT DEFAULT 0,
            total INT DEFAULT 0,
            percentage DECIMAL(5,2) DEFAULT 0,
            class_id INT,
            FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL,
            FOREIGN KEY (semester_id) REFERENCES semesters(id) ON DELETE SET NULL
        )
    """)
    
    # Teachers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            teacher_id VARCHAR(20) UNIQUE NOT NULL,
            teacher_code VARCHAR(20) UNIQUE,
            name VARCHAR(100),
            password VARCHAR(100),
            gender VARCHAR(10),
            dob DATE,
            branch VARCHAR(50),
            subjects TEXT,
            phone VARCHAR(15),
            email VARCHAR(100) UNIQUE,
            photo VARCHAR(255)
        )
    """)
    
    # Subjects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INT PRIMARY KEY AUTO_INCREMENT,
            subject_name VARCHAR(100) NOT NULL,
            branch_id INT,
            semester_id INT,
            FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE CASCADE,
            FOREIGN KEY (semester_id) REFERENCES semesters(id) ON DELETE CASCADE
        )
    """)
    
    # Teacher_Subjects mapping
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teacher_subjects (
            id INT PRIMARY KEY AUTO_INCREMENT,
            teacher_id VARCHAR(20),
            subject_id INT,
            FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
            UNIQUE KEY unique_teacher_subject (teacher_id, subject_id)
        )
    """)
    
    # Student_Subjects mapping
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_subjects (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(20),
            subject_id INT,
            UNIQUE KEY uniq_student_subject (student_id, subject_id),
            FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
        )
    """)
    
    # Marks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            id INT PRIMARY KEY AUTO_INCREMENT,
            student_id VARCHAR(20),
            subject_id INT,
            internal_exam_1 INT DEFAULT 0,
            internal_exam_2 INT DEFAULT 0,
            internal_exam_3 INT DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            UNIQUE KEY unique_student_subject (student_id, subject_id),
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
        )
    """)
    
    # Announcements table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS announcements (
            id INT AUTO_INCREMENT PRIMARY KEY,
            message TEXT,
            file VARCHAR(255),
            target_audience VARCHAR(50) DEFAULT 'all',
            created_by VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Classes table (legacy support)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            class_name VARCHAR(100)
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ All tables created")

def populate_initial_data():
    """Populate branches, semesters, subjects, and admin user"""
    print("\n📊 Populating initial data...")
    conn = get_connection('bima')
    cursor = conn.cursor()
    
    # Insert branches
    branches = [('MCA', 1), ('MBA', 2)]
    for branch_name, _ in branches:
        cursor.execute("INSERT IGNORE INTO branches (name) VALUES (%s)", (branch_name,))
    
    # Insert semesters
    for sem in range(1, 5):
        cursor.execute("INSERT IGNORE INTO semesters (sem_no) VALUES (%s)", (sem,))
    
    # Insert classes (legacy)
    classes = [
        ('MCA Sem 1',), ('MCA Sem 2',),
        ('MBA Sem 1',), ('MBA Sem 2',)
    ]
    for class_name, in classes:
        cursor.execute("INSERT IGNORE INTO classes (class_name) VALUES (%s)", (class_name,))
    
    conn.commit()
    
    # Get IDs for subjects
    cursor.execute("SELECT id FROM branches WHERE name='MCA'")
    mca_id = cursor.fetchone()[0]
    cursor.execute("SELECT id FROM branches WHERE name='MBA'")
    mba_id = cursor.fetchone()[0]
    
    # Insert subjects for MCA (all semesters)
    mca_subjects = [
        ('Programming (Python / C)', mca_id, 1),
        ('Data Structures', mca_id, 1),
        ('Computer Organization', mca_id, 1),
        ('Discrete Mathematics', mca_id, 1),
        ('Database Management Systems (DBMS)', mca_id, 1),
        ('Object-Oriented Programming (Java / C++)', mca_id, 2),
        ('Operating Systems', mca_id, 2),
        ('Software Engineering', mca_id, 2),
        ('Computer Networks', mca_id, 2),
        ('Web Technologies', mca_id, 2),
        ('Artificial Intelligence', mca_id, 3),
        ('Machine Learning / Data Science', mca_id, 3),
        ('Cloud Computing', mca_id, 3),
        ('Elective (Cybersecurity / IoT / Blockchain etc.)', mca_id, 3),
        ('Mini Project', mca_id, 3),
        ('Major Project (Full Semester)', mca_id, 4),
        ('Internship / Industrial Training', mca_id, 4),
        ('Seminar & Viva', mca_id, 4),
    ]
    
    for subject_name, branch_id, sem_no in mca_subjects:
        cursor.execute(
            "INSERT IGNORE INTO subjects (subject_name, branch_id, semester_id) SELECT %s, %s, id FROM semesters WHERE sem_no=%s",
            (subject_name, branch_id, sem_no)
        )
    
    # Insert subjects for MBA (all semesters)
    mba_subjects = [
        ('Principles of Management', mba_id, 1),
        ('Financial Accounting', mba_id, 1),
        ('Business Economics', mba_id, 1),
        ('Organizational Behavior', mba_id, 1),
        ('Business Communication', mba_id, 1),
        ('Marketing Management', mba_id, 2),
        ('Financial Management', mba_id, 2),
        ('Human Resource Management', mba_id, 2),
        ('Operations Management', mba_id, 2),
        ('Business Analytics / Research Methods', mba_id, 2),
        ('Strategic Management', mba_id, 3),
        ('Elective 1', mba_id, 3),
        ('Elective 2', mba_id, 3),
        ('Elective 3', mba_id, 3),
        ('Summer Internship Project', mba_id, 3),
        ('Advanced Electives (based on specialization)', mba_id, 4),
        ('International Business', mba_id, 4),
        ('Project / Dissertation', mba_id, 4),
        ('Viva', mba_id, 4),
    ]
    
    for subject_name, branch_id, sem_no in mba_subjects:
        cursor.execute(
            "INSERT IGNORE INTO subjects (subject_name, branch_id, semester_id) SELECT %s, %s, id FROM semesters WHERE sem_no=%s",
            (subject_name, branch_id, sem_no)
        )
    
    # Insert admin user
    admin_pwd = hash_password('admin')
    cursor.execute("INSERT IGNORE INTO admin (username, password) VALUES (%s, %s)", ('admin', admin_pwd))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Initial data loaded")

def create_sample_users():
    """Create sample admin, teacher, and student users"""
    print("\n👥 Creating sample users...")
    conn = get_connection('bima')
    cursor = conn.cursor()
    
    # Insert sample students
    students = [
        ('STU001', 'Raj Kumar', hash_password('student123'), 'Male', '2002-05-15', 'MCA', 1, 'raj@email.com', '9876543210', '9876543200'),
        ('STU002', 'Priya Singh', hash_password('student123'), 'Female', '2002-08-22', 'MCA', 1, 'priya@email.com', '9876543211', '9876543201'),
        ('STU003', 'Amit Patel', hash_password('student123'), 'Male', '2002-03-10', 'MBA', 1, 'amit@email.com', '9876543212', '9876543202'),
        ('STU004', 'Neha Sharma', hash_password('student123'), 'Female', '2002-11-30', 'MBA', 1, 'neha@email.com', '9876543213', '9876543203'),
        ('STU005', 'Vikram Gupta', hash_password('student123'), 'Male', '2002-07-18', 'MCA', 2, 'vikram@email.com', '9876543214', '9876543204'),
    ]
    
    for student_id, name, pwd, gender, dob, branch, sem, email, mobile, father_mobile in students:
        cursor.execute(
            "INSERT IGNORE INTO students (student_id, name, password, gender, dob, branch, semester, mobile, father_mobile) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (student_id, name, pwd, gender, dob, branch, sem, mobile, father_mobile)
        )
    
    # Update branch_id and semester_id for students
    cursor.execute("""
        UPDATE students s 
        JOIN branches b ON s.branch = b.name 
        SET s.branch_id = b.id 
        WHERE s.branch_id IS NULL
    """)
    
    cursor.execute("""
        UPDATE students s 
        JOIN semesters sem ON s.semester = sem.sem_no 
        SET s.semester_id = sem.id 
        WHERE s.semester_id IS NULL
    """)
    
    conn.commit()
    
    # Insert sample teachers
    teachers = [
        ('T001', 'T001', 'Dr. John doe', hash_password('teacher123'), 'Male', '1980-05-10', 'MCA', 'Data Structures,Database Management', '9999999001', 'john@email.com'),
        ('T002', 'T002', 'Prof. Sarah Williams', hash_password('teacher123'), 'Female', '1982-08-20', 'MCA', 'Web Development,Machine Learning', '9999999002', 'sarah@email.com'),
        ('T003', 'T003', 'Dr. Michael Brown', hash_password('teacher123'), 'Male', '1979-03-15', 'MBA', 'Financial Management,Marketing', '9999999003', 'michael@email.com'),
        ('T004', 'T004', 'Prof. Emily Davis', hash_password('teacher123'), 'Female', '1981-11-25', 'MBA', 'Operations,Strategy', '9999999004', 'emily@email.com'),
    ]
    
    for teacher_id, code, name, pwd, gender, dob, branch, subjects, phone, email in teachers:
        cursor.execute(
            "INSERT IGNORE INTO teachers (teacher_id, teacher_code, name, password, gender, dob, branch, subjects, phone, email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (teacher_id, code, name, pwd, gender, dob, branch, subjects, phone, email)
        )
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Sample users created:")
    print("   Admin: username='admin', password='admin'")
    print("   Teachers: T001-T004 with password='teacher123'")
    print("   Students: STU001-STU005 with password='student123'")

def sync_student_subjects():
    """Map students to their subjects"""
    print("\n🔗 Syncing student-subject mappings...")
    conn = get_connection('bima')
    cursor = conn.cursor()
    
    # Get all students
    cursor.execute("SELECT student_id, branch_id, semester_id FROM students WHERE branch_id IS NOT NULL AND semester_id IS NOT NULL")
    students = cursor.fetchall()
    
    for student_id, branch_id, semester_id in students:
        cursor.execute(
            "DELETE FROM student_subjects WHERE student_id=%s",
            (student_id,)
        )
        cursor.execute("""
            INSERT IGNORE INTO student_subjects (student_id, subject_id)
            SELECT %s, s.id FROM subjects s
            WHERE s.branch_id=%s AND s.semester_id=%s
        """, (student_id, branch_id, semester_id))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Student-subject mappings created")

def create_sample_marks():
    """Create sample marks for students"""
    print("\n📝 Creating sample marks...")
    conn = get_connection('bima')
    cursor = conn.cursor()
    
    # Get sample data
    cursor.execute("SELECT student_id FROM students LIMIT 3")
    students = cursor.fetchall()
    
    cursor.execute("SELECT id FROM subjects WHERE branch_id IN (SELECT id FROM branches WHERE name='MCA') AND semester_id IN (SELECT id FROM semesters WHERE sem_no=1) LIMIT 3")
    subjects = cursor.fetchall()
    
    # Insert sample marks
    for student_id, in students:
        for subject_id, in subjects:
            cursor.execute("""
                INSERT IGNORE INTO marks (student_id, subject_id, internal_exam_1, internal_exam_2, internal_exam_3)
                VALUES (%s, %s, %s, %s, %s)
            """, (student_id, subject_id, 18, 19, 20))
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Sample marks created")

def verify_setup():
    """Verify all tables and data"""
    print("\n✅ Verification Report:")
    conn = get_connection('bima')
    cursor = conn.cursor()
    
    tables_and_counts = [
        ("branches", "SELECT COUNT(*) FROM branches"),
        ("semesters", "SELECT COUNT(*) FROM semesters"),
        ("subjects", "SELECT COUNT(*) FROM subjects"),
        ("admin", "SELECT COUNT(*) FROM admin"),
        ("students", "SELECT COUNT(*) FROM students"),
        ("teachers", "SELECT COUNT(*) FROM teachers"),
        ("teacher_subjects", "SELECT COUNT(*) FROM teacher_subjects"),
        ("student_subjects", "SELECT COUNT(*) FROM student_subjects"),
        ("marks", "SELECT COUNT(*) FROM marks"),
        ("announcements", "SELECT COUNT(*) FROM announcements"),
    ]
    
    for table_name, query in tables_and_counts:
        cursor.execute(query)
        count = cursor.fetchone()[0]
        print(f"   {table_name:20} → {count:4} records")
    
    cursor.close()
    conn.close()

def main():
    """Main setup function"""
    print("=" * 60)
    print("🚀 ACADEMIC SYSTEM - COMPLETE PROJECT SETUP")
    print("=" * 60)
    
    try:
        create_database()
        create_tables()
        populate_initial_data()
        create_sample_users()
        sync_student_subjects()
        create_sample_marks()
        verify_setup()
        
        print("\n" + "=" * 60)
        print("✅ PROJECT SETUP COMPLETE!")
        print("=" * 60)
        print("\n📌 Quick Start:")
        print("   1. Run the Flask app: python app.py")
        print("   2. Login at http://127.0.0.1:5000")
        print("\n🔐 Test Credentials:")
        print("   Admin: admin / admin")
        print("   Teacher: T001 / teacher123")
        print("   Student: STU001 / student123")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        raise

if __name__ == "__main__":
    main()
