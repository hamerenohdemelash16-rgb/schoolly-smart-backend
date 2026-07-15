import psycopg2
from db_manager import get_connection, assign_student_to_class

def seed_test_environment():
    """Seeds a test room, a teacher, and a class to verify logic works."""
    print("\n--- Seeding Test Environment ---")
    conn = get_connection()
    if not conn:
        return None

    try:
        with conn:
            with conn.cursor() as cur:
                # 1. Clear existing test data to ensure clean runs
                cur.execute("TRUNCATE attendance, students, classes, teachers, rooms RESTART IDENTITY CASCADE;")
                
                # 2. Insert a test room with a strict capacity of 2 for rapid testing
                cur.execute("INSERT INTO rooms (room_number, max_capacity) VALUES ('Room 101', 2) RETURNING room_id;")
                room_id = cur.fetchone()[0]
                
                # 3. Insert a test teacher
                cur.execute("""
                    INSERT INTO teachers (full_name, email, department) 
                    VALUES ('Abebe Kebede', 'abebe@schoolly.com', 'Mathematics') 
                    RETURNING teacher_id;
                """)
                teacher_id = cur.fetchone()[0]
                
                # 4. Insert a class linking the teacher and room
                cur.execute("""
                    INSERT INTO classes (class_name, teacher_id, room_id) 
                    VALUES ('Grade 12 Math', %s, %s) 
                    RETURNING class_id;
                """, (teacher_id, room_id))
                class_id = cur.fetchone()[0]
                
                print(f"[SEED SUCCESS] Created Room 101 (Cap: 2) and Class ID: {class_id}")
                return class_id
    except Exception as e:
        print(f"[SEED ERROR] Failed to setup test data: {e}")
        return None
    finally:
        conn.close()

def run_stress_test(class_id):
    """Attempts to insert 3 students into a class assigned to a room with a capacity of 2."""
    print("\n--- Running Capacity Constraint Stress Test ---")
    
    # Student 1 - Should Succeed
    assign_student_to_class("Hamerenoh Demelash", "hamerenoh@schoolly.com", class_id)
    
    # Student 2 - Should Succeed
    assign_student_to_class("John Doe", "john@schoolly.com", class_id)
    
    # Student 3 - Should Be BLOCKED (Enforcing our DB constraint)
    print("\n[TESTING] Attempting to insert 3rd student into a room capped at 2...")
    success = assign_student_to_class("Jane Smith", "jane@schoolly.com", class_id)
    
    if not success:
        print("\n[PASSED] Backend perfectly defended the system from over-enrollment!")
    else:
        print("\n[FAILED] Bug detected: The system allowed over-enrollment.")

if __name__ == "__main__":
    test_class_id = seed_test_environment()
    if test_class_id:
        run_stress_test(test_class_id)