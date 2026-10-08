import os
import json
from datetime import datetime


# --------------------------------
# Paths
# --------------------------------

STUDENT_DIR = os.path.join("data", "students")
ATTENDANCE_DIR = os.path.join("data", "attendance")


# Create attendance folder if it
# does not already exist

os.makedirs(ATTENDANCE_DIR, exist_ok=True)


# --------------------------------
# Get all registered students
# --------------------------------

def get_registered_students():

    students = []

    if not os.path.exists(STUDENT_DIR):
        return students

    for name in os.listdir(STUDENT_DIR):

        student_path = os.path.join(
            STUDENT_DIR,
            name
        )

        if os.path.isdir(student_path):
            students.append(name)

    return sorted(students)


# --------------------------------
# Generate attendance
# --------------------------------

def generate_attendance(recognized_people):

    registered_students = get_registered_students()

    # Convert recognized people to a set
    # so duplicates are removed

    present_students = set(recognized_people)

    attendance = {}

    # --------------------------------
    # Compare registered students
    # with recognized students
    # --------------------------------

    for student in registered_students:

        if student in present_students:

            attendance[student] = "Present"

        else:

            attendance[student] = "Absent"

    return attendance


# --------------------------------
# Save attendance
# --------------------------------

def save_attendance(attendance):

    now = datetime.now()

    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    filename = f"attendance_{date}.json"

    filepath = os.path.join(
        ATTENDANCE_DIR,
        filename
    )

    data = {

        "date": date,

        "time": time,

        "attendance": attendance

    }


    with open(filepath, "w") as file:

        json.dump(
            data,
            file,
            indent=4
        )


    print("\nAttendance saved successfully.")

    print(f"File: {filepath}")


# --------------------------------
# Display attendance
# --------------------------------

def display_attendance(attendance):

    print("\n")
    print("=" * 40)
    print("           ATTENDANCE")
    print("=" * 40)

    present_count = 0
    absent_count = 0


    for student, status in attendance.items():

        if status == "Present":

            print(f"✓ {student:<25} PRESENT")

            present_count += 1

        else:

            print(f"✗ {student:<25} ABSENT")

            absent_count += 1


    print("=" * 40)

    print(f"Total Students : {len(attendance)}")
    print(f"Present        : {present_count}")
    print(f"Absent         : {absent_count}")

    print("=" * 40)


# --------------------------------
# Test the attendance system
# --------------------------------

if __name__ == "__main__":

    print("Testing Attendance Engine...")


    # Example recognized students

    recognized_people = [
        "Aaryan_Patidar"
    ]


    # Generate attendance

    attendance = generate_attendance(
        recognized_people
    )


    # Display attendance

    display_attendance(
        attendance
    )


    # Save attendance

    save_attendance(
        attendance
    )