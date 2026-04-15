#!/usr/bin/env python
"""Load subjects data into the database."""
import mysql.connector

conn = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='SriVishnu@143',
    database='bima'
)
cur = conn.cursor()

# Ensure branches and semesters exist
cur.execute("INSERT IGNORE INTO branches (name) VALUES ('MCA'), ('MBA')")
for sem in range(1, 5):
    cur.execute("INSERT IGNORE INTO semesters (sem_no) VALUES (%s)", (sem,))
conn.commit()

# Clear existing subjects to avoid duplicates (must clear dependent tables first)
cur.execute("DELETE FROM teacher_subjects")
cur.execute("DELETE FROM student_subjects")
cur.execute("DELETE FROM marks")
cur.execute("DELETE FROM subjects")
conn.commit()

# Get branch and semester IDs
cur.execute("SELECT id FROM branches WHERE name='MCA'")
mca_id = cur.fetchone()[0]
cur.execute("SELECT id FROM branches WHERE name='MBA'")
mba_id = cur.fetchone()[0]

# MCA Subjects
mca_subjects = [
    # Semester 1
    [('Mathematical Foundations', mca_id, 1),
     ('Programming in C', mca_id, 1),
     ('Computer Organization', mca_id, 1),
     ('Digital Logic', mca_id, 1),
     ('Communication Skills', mca_id, 1),
     ('Computer Basics', mca_id, 1)],
    # Semester 2
    [('Data Structures', mca_id, 2),
     ('Operating Systems', mca_id, 2),
     ('Database Management Systems', mca_id, 2),
     ('Object Oriented Programming (Java)', mca_id, 2),
     ('Software Engineering', mca_id, 2),
     ('Artificial Intelligence', mca_id, 2)],
    # Semester 3
    [('Computer Networks', mca_id, 3),
     ('Web Technologies', mca_id, 3),
     ('Data Mining', mca_id, 3),
     ('Mobile Computing', mca_id, 3),
     ('Cloud Computing', mca_id, 3),
     ('Machine Learning', mca_id, 3),
     ('Mini_Project', mca_id, 3)],
    # Semester 4
    [('Project Work', mca_id, 4)]
]

# MBA Subjects
mba_subjects = [
    # Semester 1
    [('Principles of Management', mba_id, 1),
     ('Financial Accounting', mba_id, 1),
     ('Business Economics', mba_id, 1),
     ('Organizational Behavior', mba_id, 1),
     ('Quantitative Methods', mba_id, 1)],
    # Semester 2
    [('Strategic Management', mba_id, 2),
     ('Financial Management', mba_id, 2),
     ('Human Resource Management', mba_id, 2),
     ('Marketing Management', mba_id, 2),
     ('Operations Management', mba_id, 2)],
    # Semester 3
    [('Business Analytics', mba_id, 3),
     ('International Business', mba_id, 3),
     ('Corporate Governance', mba_id, 3),
     ('Supply Chain Management', mba_id, 3)],
    # Semester 4
    [('Project Work', mba_id, 4)]
]

# Insert all subjects
for semester_list in mca_subjects:
    for subject_name, branch_id, semester_no in semester_list:
        cur.execute("SELECT id FROM semesters WHERE sem_no=%s", (semester_no,))
        sem_row = cur.fetchone()
        if sem_row:
            sem_id = sem_row[0]
            cur.execute(
                "INSERT INTO subjects (subject_name, branch_id, semester_id) VALUES (%s, %s, %s)",
                (subject_name, branch_id, sem_id)
            )

for semester_list in mba_subjects:
    for subject_name, branch_id, semester_no in semester_list:
        cur.execute("SELECT id FROM semesters WHERE sem_no=%s", (semester_no,))
        sem_row = cur.fetchone()
        if sem_row:
            sem_id = sem_row[0]
            cur.execute(
                "INSERT INTO subjects (subject_name, branch_id, semester_id) VALUES (%s, %s, %s)",
                (subject_name, branch_id, sem_id)
            )

conn.commit()

# Verify
cur.execute("SELECT COUNT(*) FROM subjects")
count = cur.fetchone()[0]
print(f"✅ Loaded {count} subjects successfully!")

cur.close()
conn.close()
