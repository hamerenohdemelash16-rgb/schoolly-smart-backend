import psycopg2
from psycopg2 import sql, OperationalError

# Database configuration
DB_CONFIG = {
    "dbname": "schoolly_smart",
    "user": "postgres",
    "password": "password123",  
    "host": "127.0.0.1",        
    "port": "5432"
}

def get_connection():
    """Establishes and returns a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except OperationalError as e:
        print(f"[ERROR] Could not connect to PostgreSQL: {e}")
        return None

def initialize_schema():
    """Creates the core relational tables with strict data constraints."""
    schema_queries = [
        """
        CREATE TABLE IF NOT EXISTS rooms (
            room_id SERIAL PRIMARY KEY,
            room_number VARCHAR(10) UNIQUE NOT NULL,
            max_capacity INTEGER DEFAULT 75 CHECK (max_capacity <= 75)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS teachers (
            teacher_id SERIAL PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            department VARCHAR(50) NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS classes (
            class_id SERIAL PRIMARY KEY,
            class_name VARCHAR(50) NOT NULL,
            teacher_id INTEGER REFERENCES teachers(teacher_id) ON DELETE SET NULL,
            room_id INTEGER REFERENCES rooms(room_id) ON DELETE RESTRICT
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS students (
            student_id SERIAL PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            class_id INTEGER REFERENCES classes(class_id) ON DELETE RESTRICT
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id SERIAL PRIMARY KEY,
            student_id INTEGER REFERENCES students(student_id) ON DELETE CASCADE,
            date DATE NOT NULL DEFAULT CURRENT_DATE,
            status VARCHAR(10) CHECK (status IN ('Present', 'Absent', 'Late')),
            UNIQUE(student_id, date)
        );
        """
    ]

    conn = get_connection()
    if not conn:
        return

    try:
        with conn:
            with conn.cursor() as cur:
                for query in schema_queries:
                    cur.execute(query)
        print("[SUCCESS] Schoolly Smart database schema initialized successfully!")
    except Exception as e:
        print(f"[ERROR] Schema initialization failed: {e}")
    finally:
        conn.close()

def assign_student_to_class(student_name, email, class_id):
    """
    Enforces business logic: Prevents assigning a student if the 
    class's assigned room has already reached its capacity limit.
    """
    conn = get_connection()
    if not conn:
        return False

    try:
        with conn:
            with conn.cursor() as cur:
                # 1. Check current class enrollment vs room capacity
                cur.execute("""
                    SELECT r.max_capacity, COUNT(s.student_id) as current_enrolled
                    FROM classes c
                    JOIN rooms r ON c.room_id = r.room_id
                    LEFT JOIN students s ON c.class_id = s.class_id
                    WHERE c.class_id = %s
                    GROUP BY r.max_capacity;
                """, (class_id,))
                
                result = cur.fetchone()
                if not result:
                    print("[ERROR] Class or assigned room does not exist.")
                    return False
                
                max_cap, current_enrolled = result
                
                # 2. Enforce the limit dynamically
                if current_enrolled >= max_cap:
                    print(f"[DENIED] Room capacity reached ({current_enrolled}/{max_cap}). Cannot add student.")
                    return False
                
                # 3. Insert student if under capacity
                cur.execute("""
                    INSERT INTO students (full_name, email, class_id)
                    VALUES (%s, %s, %s) RETURNING student_id;
                """, (student_name, email, class_id))
                
                new_id = cur.fetchone()[0]
                print(f"[SUCCESS] Assigned {student_name} (ID: {new_id}) to Class {class_id}. Enrollment: {current_enrolled + 1}/{max_cap}")
                return True
    except Exception as e:
        print(f"[ERROR] Database transaction failed: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("--- Initializing Schoolly Smart Backend ---")
    initialize_schema()