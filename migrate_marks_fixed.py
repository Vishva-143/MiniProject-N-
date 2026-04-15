from dotenv import load_dotenv
import os
load_dotenv()

import mysql.connector
from mysql.connector import Error

def get_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'SriVishnu@143'),
        database=os.getenv('DB_NAME', 'bima')
    )

# Marks Migration: Fixed columns → Dynamic subjects/marks (silent mode)

try:
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. FIND SUBJECT MAPPINGS (manual - based on fixed columns)
    subject_map = {
        'english': 'English',  # Will match subject_name 
        'mathematics': 'Mathematics',
        'physics': 'Physics', 
        'chemistry': 'Chemistry',
        'computer_science': 'Computer Science'  # Adjust if exact names differ
    }
    
    # 2. Migrate each student with non-zero marks
    cursor.execute("""
    SELECT student_id, english, mathematics, physics, chemistry, computer_science 
    FROM students WHERE english > 0 OR mathematics > 0 OR physics > 0 OR chemistry > 0 OR computer_science > 0
    """)
    students_with_marks = cursor.fetchall()
    
    migrated = 0
    for student_row in students_with_marks:
        student_id = student_row[0]
        marks = [student_row[1], student_row[2], student_row[3], student_row[4], student_row[5]]  # eng,math,phys,chem,cs
        
        for i, (col, subj_name) in enumerate(subject_map.items()):
            mark_total = marks[i]
            if mark_total > 0:
                # Distribute to 3 internals (avg)
                exam1, exam2, exam3 = mark_total//3, mark_total//3, mark_total - 2*(mark_total//3)
                
                # Find subject ID (first match for branch)
                cursor.execute("""
                SELECT id FROM subjects 
                WHERE subject_name LIKE %s AND branch_id = (SELECT branch_id FROM students WHERE student_id=%s)
                LIMIT 1
                """, (f"%{subj_name}%", student_id))
                subj_result = cursor.fetchone()
                
                if subj_result:
                    subject_id = subj_result[0]
                    cursor.execute("""
                    INSERT INTO marks (student_id, subject_id, internal_exam_1, internal_exam_2, internal_exam_3)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        internal_exam_1 = %s, internal_exam_2 = %s, internal_exam_3 = %s
                    """, (student_id, subject_id, exam1, exam2, exam3, exam1, exam2, exam3))
                    migrated += 1
    
    # 3. OPTIONAL: Clear old columns (commented - backup first!)
    # cursor.execute("ALTER TABLE students DROP COLUMN english, DROP COLUMN mathematics, DROP COLUMN physics, DROP COLUMN chemistry, DROP COLUMN computer_science, DROP COLUMN total, DROP COLUMN percentage")
    
    conn.commit()
    # Migration complete: {migrated} mark entries moved to dynamic table!
    # Fixed columns preserved as backup. Drop manually if no longer needed.
    
    # Verify
    cursor.execute("SELECT COUNT(*) as dynamic_marks FROM marks")
    dynamic_count = cursor.fetchone()[0]
    
except Error as e:
    print(f"Migration Error: {e}")
finally:
    if conn.is_connected():
        cursor.close()
        conn.close()

print("\nMigration done! Test with: SELECT s.name, su.subject_name, m.* FROM marks m JOIN students s ON m.student_id=s.student_id JOIN subjects su ON m.subject_id=su.id LIMIT 5")

