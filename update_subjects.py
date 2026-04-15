#!/usr/bin/env python3
"""
Update subjects in the database with the comprehensive MCA and MBA curriculum.
Run this script after the main setup to update subjects.
"""

import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="SriVishnu@143",
        database="bima"
    )

def update_subjects():
    """Update MCA and MBA subjects with comprehensive curriculum"""
    conn = get_db()
    cur = conn.cursor(buffered=True, dictionary=True)
    
    # Get branch IDs
    cur.execute("SELECT id FROM branches WHERE name='MCA'")
    mca_result = cur.fetchone()
    mca_id = mca_result["id"] if mca_result else None
    
    cur.execute("SELECT id FROM branches WHERE name='MBA'")
    mba_result = cur.fetchone()
    mba_id = mba_result["id"] if mba_result else None
    
    if not mca_id or not mba_id:
        print("❌ Branches not found. Run setup_full_project.py first.")
        return
    
    # MCA Subjects
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
    
    # MBA Subjects
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
    
    # Clear existing subjects for these branches (and related data)
    cur.execute("DELETE FROM marks WHERE subject_id IN (SELECT id FROM subjects WHERE branch_id IN (%s, %s))", (mca_id, mba_id))
    cur.execute("DELETE FROM teacher_subjects WHERE subject_id IN (SELECT id FROM subjects WHERE branch_id IN (%s, %s))", (mca_id, mba_id))
    cur.execute("DELETE FROM student_subjects WHERE subject_id IN (SELECT id FROM subjects WHERE branch_id IN (%s, %s))", (mca_id, mba_id))
    cur.execute("DELETE FROM subjects WHERE branch_id IN (%s, %s)", (mca_id, mba_id))
    conn.commit()
    print("🗑️ Cleared old subjects and related data")
    
    # Insert MCA subjects
    for subject_name, branch_id, sem_no in mca_subjects:
        cur.execute(
            "INSERT INTO subjects (subject_name, branch_id, semester_id) SELECT %s, %s, id FROM semesters WHERE sem_no=%s",
            (subject_name, branch_id, sem_no)
        )
    conn.commit()
    print(f"✅ Added {len(mca_subjects)} MCA subjects")
    
    # Insert MBA subjects
    for subject_name, branch_id, sem_no in mba_subjects:
        cur.execute(
            "INSERT INTO subjects (subject_name, branch_id, semester_id) SELECT %s, %s, id FROM semesters WHERE sem_no=%s",
            (subject_name, branch_id, sem_no)
        )
    conn.commit()
    print(f"✅ Added {len(mba_subjects)} MBA subjects")
    
    cur.close()
    conn.close()
    print("\n✨ Subject database updated successfully!")

if __name__ == "__main__":
    update_subjects()
