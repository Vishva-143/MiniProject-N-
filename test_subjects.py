#!/usr/bin/env python
"""Quick test to verify subjects are loaded and API returns data."""
import mysql.connector
import json

conn = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    password='SriVishnu@143',
    database='bima'
)
cur = conn.cursor(dictionary=True)

# Check if subjects exist
print("=" * 60)
print("Checking subjects table...")
print("=" * 60)

cur.execute("SELECT COUNT(*) as cnt FROM subjects")
count = cur.fetchone()['cnt']
print(f"Total subjects in database: {count}")

if count == 0:
    print("\n⚠️  No subjects found! Loading preload data...")
    # Read and execute preload_data.sql
    with open('preload_data.sql', 'r') as f:
        sql_content = f.read()
    
    # Split by semicolon and execute each statement
    statements = sql_content.split(';')
    for stmt in statements:
        stmt = stmt.strip()
        if stmt and not stmt.startswith('--'):
            try:
                cur.execute(stmt)
            except Exception as e:
                print(f"Warning executing statement: {e}")
    
    conn.commit()
    
    # Recount
    cur.execute("SELECT COUNT(*) as cnt FROM subjects")
    count = cur.fetchone()['cnt']
    print(f"✅ Subjects loaded! Total now: {count}")

print("\n" + "=" * 60)
print("Testing API endpoint: GET /get_subjects/MCA/Semester 1")
print("=" * 60)

# Simulate the API query
cur.execute("""
    SELECT s.id, s.subject_name, s.subject_name AS name
    FROM subjects s
    INNER JOIN branches b ON s.branch_id = b.id
    INNER JOIN semesters sem ON s.semester_id = sem.id
    WHERE b.name = %s AND sem.sem_no = %s
    ORDER BY s.subject_name
""", ('MCA', 1))

rows = cur.fetchall()
print(f"Result rows: {len(rows)}")
print("\nJSON response (as API would return):")
print(json.dumps(rows, indent=2, default=str))

cur.close()
conn.close()

print("\n✅ Test complete!")
