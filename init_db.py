import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def get_db_config():
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'SriVishnu@143'),
        'database': None  # Connect without DB first
    }

def create_database():
    config = get_db_config()
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS bima")
    cursor.close()
    conn.close()
    print("✅ Database 'bima' created/verified")

def run_schema():
    config = get_db_config()
    config['database'] = 'bima'
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    # Basic tables (flat for app compatibility)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE,
        password VARCHAR(100)
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id VARCHAR(20) UNIQUE,
        name VARCHAR(100),
        gender VARCHAR(10),
        dob DATE,
        branch VARCHAR(50),
        semester INT,
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
        password VARCHAR(100),
        class_id INT,
        email VARCHAR(100) UNIQUE
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        teacher_id VARCHAR(20) UNIQUE,
        name VARCHAR(100),
        gender VARCHAR(10),
        dob DATE,
        branch VARCHAR(50),
        subjects TEXT,
        phone VARCHAR(15),
        photo VARCHAR(255),
        password VARCHAR(100)
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS announcements (
        id INT AUTO_INCREMENT PRIMARY KEY,
        message TEXT,
        file VARCHAR(255),
        target_audience VARCHAR(50) DEFAULT 'all',
        created_by VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        class_name VARCHAR(100)
    )""")
    
    # Insert default admin
    cursor.execute("INSERT IGNORE INTO admin (username, password) VALUES ('admin', 'admin123')")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Schema tables created")

def preload_sample_data():
    config = get_db_config()
    config['database'] = 'bima'
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    
    # Sample students
    students_data = [
        ('MCA001', 'Alice Johnson', 'F', '2002-05-15', 'MCA', 1, '9876543210', '9876543200', None, 85, 92, 88, 90, 95, 450, 90.00, 'pass123', None),
        ('MCA002', 'Bob Smith', 'M', '2001-08-20', 'MCA', 1, '9876543211', '9876543201', None, 78, 85, 82, 80, 88, 413, 82.60, 'pass123', None),
    ]
    for row in students_data:
        cursor.execute("""
            INSERT IGNORE INTO students (student_id, name, gender, dob, branch, semester, mobile, father_mobile, photo, english, mathematics, physics, chemistry, computer_science, total, percentage, password, class_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, row)
    conn.commit()
    
    # Sample teachers
    cursor.execute("INSERT IGNORE INTO teachers (teacher_id, name, gender, dob, branch, subjects, phone, password) VALUES ('T001', 'Dr. Jane Doe', 'F', '1980-03-10', 'MCA', 'Math,Physics', '9876543212', 'teach123')")
    
    # Sample classes
    cursor.execute("INSERT IGNORE INTO classes (class_name) VALUES ('MCA Sem 1'),('MCA Sem 2')")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Sample data loaded")

if __name__ == '__main__':
    create_database()
    run_schema()
    preload_sample_data()
    print("🎉 DB fully initialized! Run: cp .env.example .env && python app.py")
