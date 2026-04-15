import mysql.connector
from mysql.connector import Error

from dotenv import load_dotenv
load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME', 'bima')
    )

try:
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if column exists
    cursor.execute("""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA='bima' 
        AND TABLE_NAME='teachers' 
        AND COLUMN_NAME='teacher_code'
    """)
    if not cursor.fetchone():
        cursor.execute("""
            ALTER TABLE teachers 
            ADD COLUMN teacher_code VARCHAR(20) UNIQUE AFTER teacher_id
        """)
        print("✅ Added teacher_code column")
    else:
        print("ℹ️ teacher_code column already exists")
    
    # Fix potential NULL values for existing teachers (generate if missing)
    cursor.execute("""
        UPDATE teachers 
        SET teacher_code = CONCAT('TCH', LPAD(id, 3, '0')) 
        WHERE teacher_code IS NULL OR teacher_code = ''
    """)
    updated = cursor.rowcount
    if updated > 0:
        print(f"✅ Generated teacher_code for {updated} existing teachers")
    
    # Add index
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_teacher_code ON teachers(teacher_code)")
    
    conn.commit()
    print("✅ Migration complete")
    
except Error as e:
    print(f"❌ Error: {e}")
finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()

