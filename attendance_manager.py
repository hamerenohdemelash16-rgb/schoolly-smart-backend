import psycopg2
from psycopg2.extras import execute_values
from db_manager import get_connection

def bulk_log_attendance(attendance_records):
    """
    Logs attendance for multiple students efficiently in a single batch.
    
    attendance_records: list of tuples -> [(student_id, status, date), ...]
    Example: [(1, 'Present', '2026-07-21'), (2, 'Late', '2026-07-21')]
    """
    if not attendance_records:
        print("[WARNING] No attendance records provided.")
        return False

    conn = get_connection()
    if not conn:
        return False

    # ON CONFLICT handles re-submitting attendance for the same student on the same day
    query = """
        INSERT INTO attendance (student_id, status, date)
        VALUES %s
        ON CONFLICT (student_id, date) 
        DO UPDATE SET status = EXCLUDED.status;
    """

    try:
        with conn:
            with conn.cursor() as cur:
                execute_values(cur, query, attendance_records)
        print(f"[SUCCESS] Bulk attendance updated for {len(attendance_records)} record(s).")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to log bulk attendance: {e}")
        return False
    finally:
        conn.close()

def get_class_attendance_summary(class_id, target_date=None):
    """
    Computes aggregated attendance counts and attendance rate (%) for a given class.
    """
    conn = get_connection()
    if not conn:
        return None

    query = """
        SELECT 
            COUNT(a.attendance_id) as total_logged,
            COUNT(CASE WHEN a.status = 'Present' THEN 1 END) as present_count,
            COUNT(CASE WHEN a.status = 'Absent' THEN 1 END) as absent_count,
            COUNT(CASE WHEN a.status = 'Late' THEN 1 END) as late_count
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        WHERE s.class_id = %s
    """
    params = [class_id]

    if target_date:
        query += " AND a.date = %s"
        params.append(target_date)

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                row = cur.fetchone()
                
                if row and row[0] > 0:
                    total, present, absent, late = row
                    rate = (present / total) * 100
                    return {
                        "total_logged": total,
                        "present": present,
                        "absent": absent,
                        "late": late,
                        "attendance_rate_pct": round(rate, 2)
                    }
                else:
                    print("[INFO] No attendance records found for the specified parameters.")
                    return None
    except Exception as e:
        print(f"[ERROR] Summary calculation failed: {e}")
        return None
    finally:
        conn.close()

if __name__ == "__main__":
    print("--- Testing Attendance Manager Engine ---")
    
    # Quick test batch using existing student IDs 1 and 2
    test_batch = [
        (1, "Present", "2026-07-21"),
        (2, "Late", "2026-07-21")
    ]
    
    if bulk_log_attendance(test_batch):
        summary = get_class_attendance_summary(class_id=1, target_date="2026-07-21")
        print("\nClass 1 Daily Metrics:", summary)