from db_manager import get_connection

def get_at_risk_students(threshold_pct=75.0):
    """
    Identifies students whose attendance rate falls below a given percentage.
    Uses SQL aggregations (COUNT, HAVING, ROUND) to perform the math directly on the database engine.
    """
    conn = get_connection()
    if not conn:
        return []

    query = """
        SELECT 
            s.student_id,
            s.full_name,
            s.email,
            COUNT(a.attendance_id) as total_days,
            COUNT(CASE WHEN a.status = 'Present' THEN 1 END) as days_present,
            ROUND((COUNT(CASE WHEN a.status = 'Present' THEN 1 END)::numeric / COUNT(a.attendance_id)) * 100, 2) as attendance_rate
        FROM students s
        JOIN attendance a ON s.student_id = a.student_id
        GROUP BY s.student_id, s.full_name, s.email
        HAVING (COUNT(CASE WHEN a.status = 'Present' THEN 1 END)::numeric / COUNT(a.attendance_id)) * 100 < %s
        ORDER BY attendance_rate ASC;
    """

    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(query, (threshold_pct,))
                rows = cur.fetchall()
                
                at_risk_list = []
                for row in rows:
                    at_risk_list.append({
                        "student_id": row[0],
                        "name": row[1],
                        "email": row[2],
                        "total_days": row[3],
                        "days_present": row[4],
                        "attendance_rate_pct": float(row[5])
                    })
                return at_risk_list
    except Exception as e:
        print(f"[ERROR] Analytics query failed: {e}")
        return []
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("--- Running At-Risk Attendance Analytics Engine ---")
    
    # Query for any students with less than 75% attendance rate
    threshold = 75.0
    at_risk = get_at_risk_students(threshold_pct=threshold)
    
    print(f"\n[ALERT] Found {len(at_risk)} student(s) below {threshold}% attendance threshold:\n")
    for student in at_risk:
        print(f" • ID {student['student_id']}: {student['name']} ({student['email']})")
        print(f"   Attendance Rate: {student['attendance_rate_pct']}% ({student['days_present']}/{student['total_days']} days present)\n")