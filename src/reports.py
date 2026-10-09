from src.database import (
    initialize_database,
    get_connection
)


# ==========================================
# DISPLAY ALL ATTENDANCE RECORDS
# ==========================================

def show_all_records():

    with get_connection() as connection:

        records = connection.execute("""
            SELECT
                student_name,
                attendance_date,
                attendance_time,
                status
            FROM attendance
            ORDER BY attendance_date DESC,
                     attendance_time DESC,
                     student_name
        """).fetchall()

    print("\n" + "=" * 75)
    print("                    ATTENDANCE HISTORY")
    print("=" * 75)

    if not records:

        print("No attendance records found.")

    else:

        print(
            f"{'Student':<25}"
            f"{'Date':<15}"
            f"{'Time':<12}"
            f"{'Status'}"
        )

        print("-" * 75)

        for name, date, time, status in records:

            print(
                f"{name:<25}"
                f"{date:<15}"
                f"{time:<12}"
                f"{status}"
            )

    print("=" * 75)


# ==========================================
# DISPLAY ONE STUDENT'S SUMMARY
# ==========================================

def show_student_summary():

    student_name = input(
        "\nEnter student name: "
    ).strip()

    if not student_name:

        print("Student name cannot be empty.")
        return

    with get_connection() as connection:

        result = connection.execute("""
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
        """, (student_name,)).fetchone()

    total_days = result[0] or 0
    present_days = result[1] or 0
    absent_days = total_days - present_days

    percentage = (
        present_days / total_days * 100
        if total_days > 0
        else 0
    )

    print("\n" + "=" * 45)
    print("             STUDENT SUMMARY")
    print("=" * 45)

    print(f"Student          : {student_name}")
    print(f"Recorded days    : {total_days}")
    print(f"Present days     : {present_days}")
    print(f"Absent days      : {absent_days}")
    print(f"Attendance       : {percentage:.2f}%")

    if total_days == 0:

        print("Status           : No records available")

    elif percentage >= 75:

        print("Status           : Above 75% attendance")

    else:

        print("Status           : Below 75% attendance")

    print("=" * 45)


# ==========================================
# DISPLAY ATTENDANCE FOR A DATE
# ==========================================

def show_attendance_by_date():

    date = input(
        "\nEnter date (YYYY-MM-DD): "
    ).strip()

    with get_connection() as connection:

        records = connection.execute("""
            SELECT
                student_name,
                attendance_time,
                status
            FROM attendance
            WHERE attendance_date = ?
            ORDER BY student_name
        """, (date,)).fetchall()

    print(f"\nAttendance for {date}")
    print("-" * 55)

    if not records:

        print("No records found for this date.")

    else:

        for name, time, status in records:

            print(
                f"{name:<25} {time:<12} {status}"
            )

    print("-" * 55)


# ==========================================
# REPORT MENU
# ==========================================

def main():

    initialize_database()

    while True:

        print("\n")
        print("=" * 45)
        print("         ATTENDANCE REPORTS")
        print("=" * 45)

        print("1. View all attendance records")
        print("2. View student attendance summary")
        print("3. View attendance by date")
        print("4. Exit")

        choice = input(
            "\nChoose an option: "
        ).strip()

        if choice == "1":

            show_all_records()

        elif choice == "2":

            show_student_summary()

        elif choice == "3":

            show_attendance_by_date()

        elif choice == "4":

            print("Exiting reports.")
            break

        else:

            print("Invalid choice. Try again.")


if __name__ == "__main__":

    main()