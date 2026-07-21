import random
from datetime import date, timedelta
from db_manager import get_connection
from attendance_manager import bulk_log_attendance

FIRST_NAMES = ["Abebe", "Kebede", "Tigist", "Mulugeta", "Haile", "Birtukan", "Dawit", "Selam", "Yonas", "Lidet"]
LAST_NAMES = ["Bekele", "Tadesse", "Alemu", "Worku", "Desta", "Girma", "Kassaye", "Tekle", "Demissie", "Assefa"]

def generate_mock_students(count=20):
    """
    Generates mock student profiles in the database.
    """
    conn = get_connection()
    if not conn:
        return []

    student_ids = []
    try:
        with conn:
            with conn.cursor() as cur:
                for _ in range(count):
                    fname = random.choice(FIRST_NAMES)
                    lname = random.choice(LAST_NAMES)
                    full_name = f"{fname} {lname}"
                    email = f"{fname.lower()}.{lname.lower()}{random.randint(100, 999)}@school.edu"
                    
                    cur.execute(
                        "INSERT INTO students (full_name, email) VALUES (%s, %s) RETURNING student_id;",
                        (full_name, email)
                    )
                    student_id = cur.fetchone()[0]
                    student_ids.append(student_id)
        print(f"[SUCCESS] Created {len(student_ids)} mock students.")
        return student_ids
    except Exception as e:
        print(f"[ERROR] Failed to seed students: {e}")
        return []
    finally:
        if conn:
            conn.close()

def generate_mock_attendance(student_ids, days=5):
    """
    Generates multi-day attendance history for all provided student IDs.
    """
    statuses = ["Present", "Present", "Present", "Late", "Absent"]
    today = date.today()
    all_records = []

    for day_offset in range(days):
        record_date = str(today - timedelta(days=day_offset))
        for s_id in student_ids:
            status = random.choice(statuses)
            all_records.append((s_id, status, record_date))

    if bulk_log_attendance(all_records):
        print(f"[SUCCESS] Seeded {len(all_records)} attendance logs across {days} school days.")

if __name__ == "__main__":
    print("--- Running Mock Data Generator ---")
    created_ids = generate_mock_students(count=20)
    if created_ids:
        generate_mock_attendance(created_ids, days=5)