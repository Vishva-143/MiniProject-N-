-- Dynamic Academic Schema for BIMA DB
-- Run: mysql -u root -p bima < schema_academic.sql

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

-- 3. Students FKs: Manually run if columns missing:
-- ALTER TABLE students ADD COLUMN branch_id INT AFTER semester;
-- ALTER TABLE students ADD COLUMN semester_id INT AFTER branch_id;
-- ALTER TABLE students ADD FOREIGN KEY (branch_id) REFERENCES branches(id);
-- ALTER TABLE students ADD FOREIGN KEY (semester_id) REFERENCES semesters(id);

-- Note: Keep old marks fields for migration if needed. New system uses marks table.
-- student_id VARCHAR PK referenced in marks.student_id

-- 4. Subjects
CREATE TABLE IF NOT EXISTS subjects (
  id INT PRIMARY KEY AUTO_INCREMENT,
  subject_name VARCHAR(100) NOT NULL,
  branch_id INT,
  semester_id INT,
  FOREIGN KEY (branch_id) REFERENCES branches(id),
  FOREIGN KEY (semester_id) REFERENCES semesters(id)
);

-- 5. Teacher_Subjects mapping
CREATE TABLE IF NOT EXISTS teacher_subjects (
  id INT PRIMARY KEY AUTO_INCREMENT,
  teacher_id VARCHAR(20),
  subject_id INT,
  FOREIGN KEY (subject_id) REFERENCES subjects(id),
  UNIQUE KEY unique_teacher_subject (teacher_id, subject_id)
);

-- 6. Marks (student_id as VARCHAR to match students.student_id)
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

-- Add FKs to students if missing (safe)
SET @alter1 = 0;
SET @alter2 = 0;

SELECT COUNT(*) INTO @has_branch_id FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA='bima' AND TABLE_NAME='students' AND COLUMN_NAME='branch_id';
SELECT COUNT(*) INTO @has_semester_id FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA='bima' AND TABLE_NAME='students' AND COLUMN_NAME='semester_id';

SET @sql1 = IF(@has_branch_id = 0, 'ALTER TABLE students ADD COLUMN branch_id INT AFTER semester;', 'SELECT \"branch_id exists\"');
PREPARE stmt1 FROM @sql1;
EXECUTE stmt1;
DEALLOCATE PREPARE stmt1;

SET @sql2 = IF(@has_semester_id = 0, 'ALTER TABLE students ADD COLUMN semester_id INT AFTER branch_id;', 'SELECT \"semester_id exists\"');
PREPARE stmt2 FROM @sql2;
EXECUTE stmt2;
DEALLOCATE PREPARE stmt2;

-- Add FK constraints (safe - skip if exist)
ALTER TABLE students ADD CONSTRAINT fk_student_branch FOREIGN KEY (branch_id) REFERENCES branches(id) ON DELETE SET NULL;
ALTER TABLE students ADD CONSTRAINT fk_student_semester FOREIGN KEY (semester_id) REFERENCES semesters(id) ON DELETE SET NULL;

-- Migration: Populate FKs from string fields (if populated)
UPDATE students s 
JOIN branches b ON s.branch = b.name 
SET s.branch_id = b.id;

UPDATE students s 
JOIN semesters sem ON s.semester = sem.sem_no 
SET s.semester_id = sem.id;

-- Indexes for performance
CREATE INDEX idx_students_branch_sem ON students(branch_id, semester_id);
CREATE INDEX idx_marks_student ON marks(student_id);
CREATE INDEX idx_marks_subject ON marks(subject_id);

-- Verify migration
SELECT 'Migration complete' as status, 
       COUNT(*) as students_with_branch_sem 
FROM students WHERE branch_id IS NOT NULL AND semester_id IS NOT NULL;

-- TEACHER TABLE UPDATES for new features
-- Add auto-increment ID PK (keep teacher_id as unique for login)
ALTER TABLE teachers ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST;
ALTER TABLE teachers ADD UNIQUE KEY unique_teacher_id (teacher_id);

-- Add required fields
ALTER TABLE teachers ADD COLUMN email VARCHAR(100) UNIQUE AFTER phone;
ALTER TABLE teachers ADD COLUMN subject VARCHAR(100) AFTER phone;

-- Indexes
CREATE INDEX idx_teachers_email ON teachers(email);
CREATE INDEX idx_teachers_phone ON teachers(phone);
CREATE INDEX idx_teachers_teacher_code ON teachers(teacher_code);

-- Add Teacher Registration Upgrade fields (safe - skip if exist)
SET @has_teacher_code = 0;
SET @has_gender = 0;
SET @has_dob = 0; 
SET @has_photo = 0;

SELECT COUNT(*) INTO @has_teacher_code FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA='bima' AND TABLE_NAME='teachers' AND COLUMN_NAME='teacher_code';
SELECT COUNT(*) INTO @has_gender FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA='bima' AND TABLE_NAME='teachers' AND COLUMN_NAME='gender';
SELECT COUNT(*) INTO @has_dob FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA='bima' AND TABLE_NAME='teachers' AND COLUMN_NAME='dob';
SELECT COUNT(*) INTO @has_photo FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA='bima' AND TABLE_NAME='teachers' AND COLUMN_NAME='photo';

SET @sql_tc = IF(@has_teacher_code = 0, 'ALTER TABLE teachers ADD COLUMN teacher_code VARCHAR(20) UNIQUE AFTER teacher_id;', 'SELECT \"teacher_code exists\"');
PREPARE stmt_tc FROM @sql_tc; EXECUTE stmt_tc; DEALLOCATE PREPARE stmt_tc;

SET @sql_gender = IF(@has_gender = 0, 'ALTER TABLE teachers ADD COLUMN gender VARCHAR(10) AFTER name;', 'SELECT \"gender exists\"');
PREPARE stmt_gender FROM @sql_gender; EXECUTE stmt_gender; DEALLOCATE PREPARE stmt_gender;

SET @sql_dob = IF(@has_dob = 0, 'ALTER TABLE teachers ADD COLUMN dob DATE AFTER gender;', 'SELECT \"dob exists\"');
PREPARE stmt_dob FROM @sql_dob; EXECUTE stmt_dob; DEALLOCATE PREPARE stmt_dob;

SET @sql_photo = IF(@has_photo = 0, 'ALTER TABLE teachers ADD COLUMN photo VARCHAR(255) AFTER dob;', 'SELECT \"photo exists\"');
PREPARE stmt_photo FROM @sql_photo; EXECUTE stmt_photo; DEALLOCATE PREPARE stmt_photo;

SELECT 'Teachers table updated' as status, 
       COUNT(*) as teacher_count FROM teachers;
