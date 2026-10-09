import sqlite3
import os
from datetime import datetime


# --------------------------------
# Database configuration
# --------------------------------

DATABASE_DIR = "data"
DATABASE_PATH = os.path.join(
    DATABASE_DIR,
    "attendance.db"
)


# --------------------------------
# Connect to database
# --------------------------------

def get_connection():

    os.makedirs(
        DATABASE_DIR,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


# --------------------------------
# Create attendance table
# --------------------------------

def initialize_database():

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_name TEXT NOT NULL,
                attendance_date TEXT NOT NULL,
                attendance_time TEXT NOT NULL,
                status TEXT NOT NULL
                    CHECK(status IN ('Present', 'Absent')),
                UNIQUE(student_name, attendance_date)
            )
        """)

    print("Database initialized successfully.")


# --------------------------------
# Save attendance records
# --------------------------------

def save_attendance(attendance):

    now = datetime.now()

    attendance_date = now.strftime(
        "%Y-%m-%d"
    )

    attendance_time = now.strftime(
        "%H:%M:%S"
    )

    records = []

    for student_name, status in attendance.items():

        records.append((
            student_name,
            attendance_date,
            attendance_time,
            status
        ))

    with get_connection() as connection:

        connection.executemany("""
            INSERT INTO attendance (
                student_name,
                attendance_date,
                attendance_time,
                status
            )
            VALUES (?, ?, ?, ?)

            ON CONFLICT(student_name, attendance_date)
            DO UPDATE SET
                attendance_time = excluded.attendance_time,
                status = excluded.status
        """, records)

    print("Attendance saved to SQLite successfully.")
    print(f"Database: {DATABASE_PATH}")


# --------------------------------
# View attendance history
# --------------------------------

def get_attendance_history(student_name=None):

    query = """
        SELECT
            student_name,
            attendance_date,
            attendance_time,
            status
        FROM attendance
    """

    parameters = ()

    if student_name:

        query += """
            WHERE student_name = ?
        """

        parameters = (student_name,)

    query += """
        ORDER BY attendance_date DESC,
                 attendance_time DESC,
                 student_name
    """

    with get_connection() as connection:

        return connection.execute(
            query,
            parameters
        ).fetchall()


# --------------------------------
# Display attendance history
# --------------------------------

def display_history(student_name=None):

    records = get_attendance_history(
        student_name
    )

    print("\n" + "=" * 75)
    print("ATTENDANCE HISTORY")
    print("=" * 75)

    if not records:

        print("No attendance records found.")

    else:

        for name, date, time, status in records:

            print(
                f"{name:<25} "
                f"{date:<12} "
                f"{time:<10} "
                f"{status}"
            )

    print("=" * 75)


# --------------------------------
# Calculate attendance summary
# --------------------------------

def get_attendance_summary(student_name):

    query = """
        SELECT
            COUNT(*),
            SUM(
                CASE
                    WHEN status = 'Present' THEN 1
                    ELSE 0
                END
            )
        FROM attendance
        WHERE student_name = ?
    """

    with get_connection() as connection:

        result = connection.execute(
            query,
            (student_name,)
        ).fetchone()

    total_days = result[0] or 0
    present_days = result[1] or 0

    absent_days = total_days - present_days

    percentage = (
        present_days / total_days * 100
        if total_days > 0
        else 0
    )

    return {
        "student": student_name,
        "total_days": total_days,
        "present_days": present_days,
        "absent_days": absent_days,
        "percentage": round(percentage, 2)
    }


# --------------------------------
# Run database module directly
# --------------------------------

if __name__ == "__main__":

    initialize_database()

    display_history()