import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def get_config():
    config = {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME', 'bima')
    }
    return config

print("Running academic schema setup...")

config = get_config()
conn = mysql.connector.connect(**config)
cursor = conn.cursor()

# Execute schema_academic.sql content directly
schema_sql = """
-- [Content from schema_academic.sql pasted here - all CREATE TABLE, ALTER, UPDATE statements]
-- Dynamic Academic Schema for BIMA DB
USE bima;

-- 1. Branches
CREATE TABLE IF NOT EXISTS branches (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(50) UNIQUE NOT NULL
);

-- 2. Semesters
CREATE TABLE IF NOT EXISTS semesters (
  id INT PRIMARY KEY AUTO_INCREMENT,
  sem_no INT NOT NULL
);

-- 3. Subjects
CREATE TABLE IF NOT EXISTS subjects (
  id INT PRIMARY KEY AUTO_INCREMENT,
  subject_name VARCHAR(100) NOT NULL,
  branch_id INT,
  semester_id INT,
  FOREIGN KEY (branch_id) REFERENCES branches(id),
  FOREIGN KEY (semester_id) REFERENCES semesters(id)
);

-- 4. Teacher_Subjects mapping
CREATE TABLE IF NOT EXISTS teacher_subjects (
  id INT PRIMARY KEY AUTO_INCREMENT,
  teacher_id VARCHAR(20),
  subject_id INT,
  FOREIGN KEY (subject_id) REFERENCES subjects(id),
  UNIQUE KEY unique_teacher_subject (teacher_id, subject_id)
);

-- 5. Marks 
CREATE TABLE IF NOT EXISTS marks (
  id INT PRIMARY KEY AUTO_INCREMENT,
  student_id VARCHAR(20),
  subject_id INT,
  internal_exam_1 INT DEFAULT 0,
  internal_exam_2 INT DEFAULT 0,
  internal_exam_3 INT DEFAULT 0,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (student_id) REFERENCES students(student_id),
  FOREIGN KEY (subject_id) REFERENCES subjects(id)
);

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_students_branch_sem ON students(branch_id, semester_id);
CREATE INDEX IF NOT EXISTS idx_marks_student ON marks(student_id);
CREATE INDEX IF NOT EXISTS idx_marks_subject ON marks(subject_id);

-- Sample data population
INSERT IGNORE INTO branches (name) VALUES ('MCA'), ('BTech'), ('BSc');
INSERT IGNORE INTO semesters (sem_no) VALUES (1), (2), (3), (4), (5), (6);
INSERT IGNORE INTO subjects (subject_name, branch_id, semester_id) VALUES 
('Mathematics', 1, 1), ('Physics', 1, 1), ('Programming', 1, 1),
('Data Structures', 1, 2), ('Database', 1, 2);

print('✅ Schema and sample data ready');
"""

try:
    for statement in schema_sql.split(';'):
        if statement.strip():
            cursor.execute(statement)
    conn.commit()
    print("✅ Schema applied successfully")
except Exception as e:
    print(f"Schema error: {e}")

finally:
    cursor.close()
    conn.close()
print("Run: python run_schema.py then python init_db.py for full setup")
