
import mysql.connector
import bcrypt

import os
def get_db_connection():
    from dotenv import load_dotenv
    load_dotenv()
    config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME', 'bima')
    }
    return mysql.connector.connect(**config)

# Hash plain passwords
passwords = {
    'admin': 'admin123',
    'T001': 'teach123',
    'MCA001': 'pass123'
}

conn = get_db_connection()
cursor = conn.cursor()

for user_id, plain_pw in passwords.items():
    hashed = bcrypt.hashpw(plain_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Update admin
    cursor.execute("UPDATE admin SET password = %s WHERE username = %s", (hashed, user_id))
    
    # Update teachers
    cursor.execute("UPDATE teachers SET password = %s WHERE teacher_id = %s", (hashed, user_id))
    
    # Update students
    cursor.execute("UPDATE students SET password = %s WHERE student_id = %s", (hashed, user_id))
    
    updated = cursor.rowcount
    print(f"Updated {user_id}: {updated} rows")

conn.commit()
cursor.close()
conn.close()
print("✅ Passwords hashed successfully")

