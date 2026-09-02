from db_manager import get_connection


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id SERIAL PRIMARY KEY,
            class_name VARCHAR(100) NOT NULL
        );
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE,
            class_id INT REFERENCES classes(id)
        );
        CREATE TABLE IF NOT EXISTS attendance (
            id SERIAL PRIMARY KEY,
            student_id INT REFERENCES students(id) ON DELETE CASCADE,
            date DATE NOT NULL,
            status VARCHAR(20) NOT NULL
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    init_db()