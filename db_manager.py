import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

def get_connection():
    env_path = Path(__file__).resolve().parent / '.env'
    load_dotenv(dotenv_path=env_path, override=True)
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError(
            f"DATABASE_URL is missing or empty after loading {env_path}."
        )
    return psycopg2.connect(db_url)

def assign_student_to_class(student_id, class_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE students SET class_id = %s WHERE id = %s;",
        (class_id, student_id)
    )
    conn.commit()
    cursor.close()
    conn.close()