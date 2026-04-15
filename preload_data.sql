-- Preload Academic Data for Dynamic System
-- Run AFTER schema_academic.sql: mysql -u root -p bima < preload_data.sql

USE bima;

-- 0. Branches & Semesters (required for subjects) - idempotent
INSERT IGNORE INTO branches (name) VALUES ('MCA'), ('MBA');
INSERT IGNORE INTO semesters (sem_no) VALUES (1),(2),(3),(4);

-- Insert Semesters 1-4
INSERT IGNORE INTO semesters (sem_no) VALUES (1),(2),(3),(4);

-- MCA Subjects (branch_id=1)
-- Sem 1
INSERT INTO subjects (subject_name, branch_id, semester_id) VALUES
('Mathematical Foundations', 1, 1),
('Programming in C', 1, 1),
('Computer Organization', 1, 1),
('Digital Logic', 1, 1),
('Communication Skills', 1, 1),
('Computer Basics', 1, 1);

-- Sem 2
INSERT INTO subjects (subject_name, branch_id, semester_id) VALUES
('Data Structures', 1, 2),
('Operating Systems', 1, 2),
('Database Management Systems', 1, 2),
('Object Oriented Programming (Java)', 1, 2),
('Software Engineering', 1, 2),
('Artificial Intelligence', 1, 2);

-- Sem 3
INSERT INTO subjects (subject_name, branch_id, semester_id) VALUES
('Computer Networks', 1, 3),
('Web Technologies', 1, 3),
('Data Mining', 1, 3),
('Mobile Computing', 1, 3),
('Cloud Computing', 1, 3),
('Machine Learning', 1, 3),
('Mini_Project', 1, 3);

-- Sem 4
INSERT INTO subjects (subject_name, branch_id, semester_id) VALUES
('Project Work', 1, 4);

-- MBA Subjects (branch_id=2)
-- Sem 1
INSERT INTO subjects (subject_name, branch_id, semester_id) VALUES
('Principles of Management', 2, 1),
('Financial Accounting', 2, 1),
('Business Economics', 2, 1),
('Marketing Management', 2, 1),
('Organizational Behavior', 2, 1);

-- Sem 2
INSERT INTO subjects (subject_name, branch_id, semester_id) VALUES
('Human Resource Management', 2, 2),
('Financial Management', 2, 2),
('Operations Management', 2, 2),
('Business Research Methods', 2, 2),
('Management Information Systems', 2, 2);

-- Sem 3
INSERT INTO subjects (subject_name, branch_id, semester_id) VALUES
('Strategic Management', 2, 3),
('International Business', 2, 3),
('Entrepreneurship Development', 2, 3),
('Supply Chain Management', 2, 3),
('Business Analytics', 2, 3);

-- Sem 4
INSERT INTO subjects (subject_name, branch_id, semester_id) VALUES
('Corporate Governance', 2, 4),
('Project Management', 2, 4),
('Digital Marketing', 2, 4),
('Leadership & Change Management', 2, 4),
('Project Work', 2, 4);

-- SAMPLE DATA FOR APP
INSERT IGNORE INTO admin (username, password) VALUES ('admin', 'admin123');

INSERT IGNORE INTO teachers (teacher_id, teacher_code, name, password, gender, dob, branch, subjects, phone, email, subject, photo) VALUES
('T001', 'T001', 'Dr. Jane Doe', 'teach123', 'F', '1980-03-10', 'MCA', 'Math, Physics', '9876543212', 'jane.doe@university.edu', 'Mathematics', NULL),
('T002', 'T002', 'Prof. John Smith', 'teach123', 'M', '1975-07-22', 'MCA', 'Data Structures, AI', '9876543213', 'john.smith@university.edu', 'Data Structures', NULL);

INSERT IGNORE INTO students (student_id, password, name, gender, dob, branch, semester, mobile, father_mobile, photo, english, mathematics, physics, chemistry, computer_science, total, percentage) VALUES
('MCA001', 'pass123', 'Alice Johnson', 'F', '2002-05-15', 'MCA', 1, '9876543210', '9876543200', NULL, 85, 92, 88, 90, 95, 450, 90.00),
('MCA002', 'pass123', 'Bob Smith', 'M', '2001-08-20', 'MCA', 1, '9876543211', '9876543201', NULL, 78, 85, 82, 80, 88, 413, 82.60),
('MCA003', 'pass123', 'Carol Davis', 'F', '2002-11-30', 'MCA', 1, '9876543214', '9876543203', NULL, 65, 72, 68, 70, 75, 350, 70.00),
('MCA004', 'pass123', 'David Wilson', 'M', '2003-02-14', 'MCA', 2, '9876543215', '9876543204', NULL, 92, 88, 95, 90, 93, 458, 91.60);

INSERT IGNORE INTO classes (class_name) VALUES ('MCA Sem 1'), ('MCA Sem 2');

INSERT IGNORE INTO announcements (message, file, target_audience, created_by) VALUES
('Welcome to Semester 1!', NULL, 'all', 'admin'),
('Math assignment due Friday', NULL, 'students', 'T001');
