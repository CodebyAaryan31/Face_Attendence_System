import cv2
import os
import json
from datetime import datetime


# ==========================================
# PATHS
# ==========================================

MODEL_PATH = os.path.join(
    "data",
    "encodings",
    "trainer.yml"
)

LABEL_PATH = os.path.join(
    "data",
    "encodings",
    "labels.json"
)

STUDENT_DIR = os.path.join(
    "data",
    "students"
)

ATTENDANCE_DIR = os.path.join(
    "data",
    "attendance"
)


# Create attendance folder
os.makedirs(
    ATTENDANCE_DIR,
    exist_ok=True
)


# ==========================================
# CHECK REQUIRED FILES
# ==========================================

if not os.path.exists(MODEL_PATH):

    print("ERROR: trainer.yml not found.")

    print("Run:")
    print("python src/train_model.py")

    exit()


if not os.path.exists(LABEL_PATH):

    print("ERROR: labels.json not found.")

    print("Run:")
    print("python src/train_model.py")

    exit()


# ==========================================
# LOAD FACE DETECTOR
# ==========================================

cascade_path = (
    cv2.data.haarcascades
    + "haarcascade_frontalface_default.xml"
)

face_detector = cv2.CascadeClassifier(
    cascade_path
)


# ==========================================
# LOAD LBPH MODEL
# ==========================================

recognizer = cv2.face.LBPHFaceRecognizer_create()

recognizer.read(
    MODEL_PATH
)


# ==========================================
# LOAD STUDENT LABELS
# ==========================================

with open(
    LABEL_PATH,
    "r"
) as file:

    labels = json.load(file)


# ==========================================
# GET REGISTERED STUDENTS
# ==========================================

registered_students = []

if os.path.exists(STUDENT_DIR):

    for name in os.listdir(STUDENT_DIR):

        student_path = os.path.join(
            STUDENT_DIR,
            name
        )

        if os.path.isdir(student_path):

            registered_students.append(
                name
            )


registered_students.sort()


# ==========================================
# START CAMERA
# ==========================================

camera = cv2.VideoCapture(0)


if not camera.isOpened():

    print("ERROR: Could not open camera.")

    exit()


print()
print("=" * 50)
print("       FACE ATTENDANCE SCANNER")
print("=" * 50)

print()
print("Registered Students:")

for student in registered_students:

    print("-", student)


print()
print("Press Q to finish scanning.")
print("=" * 50)


# ==========================================
# PEOPLE RECOGNIZED DURING SCAN
# ==========================================

recognized_people = set()


# ==========================================
# CAMERA LOOP
# ==========================================

while True:

    ret, frame = camera.read()


    if not ret:

        print(
            "ERROR: Could not read camera."
        )

        break


    # Mirror camera
    frame = cv2.flip(
        frame,
        1
    )


    # Convert to grayscale
    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )


    # Detect faces
    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80)
    )


    # ======================================
    # RECOGNIZE EVERY FACE
    # ======================================

    for (
        x,
        y,
        w,
        h
    ) in faces:

        # Crop face
        face = gray[
            y:y + h,
            x:x + w
        ]


        # Resize to training size
        face = cv2.resize(
            face,
            (200, 200)
        )


        # Predict identity
        label, confidence = recognizer.predict(
            face
        )


        # ==================================
        # CHECK CONFIDENCE
        # ==================================

        if confidence < 70:

            name = labels.get(
                str(label),
                "Unknown"
            )

            # Add recognized person
            if name in registered_students:
                recognized_people.add(name)

            

            box_color = (
                0,
                255,
                0
            )

        else:

            name = "Unknown"

            box_color = (
                0,
                0,
                255
            )


        # ==================================
        # DRAW FACE BOX
        # ==================================

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            box_color,
            2
        )


        # ==================================
        # DISPLAY NAME
        # ==================================

        cv2.putText(
            frame,
            name,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            box_color,
            2
        )


        # ==================================
        # DISPLAY CONFIDENCE
        # ==================================

        cv2.putText(
            frame,
            f"{confidence:.1f}",
            (
                x,
                y + h + 25
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            box_color,
            2
        )


    # ======================================
    # DISPLAY SCAN INFORMATION
    # ======================================

    cv2.putText(
        frame,
        f"Faces: {len(faces)}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )


    cv2.putText(
        frame,
        f"Present: {len(recognized_people)}",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )


    cv2.putText(
        frame,
        "Press Q to finish",
        (20, 105),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )


    # ======================================
    # SHOW CAMERA
    # ======================================

    cv2.imshow(
        "Face Attendance Scanner",
        frame
    )


    # ======================================
    # QUIT SCANNING
    # ======================================

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


# ==========================================
# STOP CAMERA
# ==========================================

camera.release()

cv2.destroyAllWindows()


# ==========================================
# GENERATE ATTENDANCE
# ==========================================

attendance = {}


for student in registered_students:

    if student in recognized_people:

        attendance[student] = "Present"

    else:

        attendance[student] = "Absent"


# ==========================================
# DISPLAY ATTENDANCE
# ==========================================

print()
print("=" * 50)
print("             ATTENDANCE RESULT")
print("=" * 50)


present_count = 0
absent_count = 0


for student, status in attendance.items():

    if status == "Present":

        print(
            f"✓ {student:<25} PRESENT"
        )

        present_count += 1

    else:

        print(
            f"✗ {student:<25} ABSENT"
        )

        absent_count += 1


print("=" * 50)

print(
    f"Total Students : {len(attendance)}"
)

print(
    f"Present        : {present_count}"
)

print(
    f"Absent         : {absent_count}"
)

print("=" * 50)


# ==========================================
# SAVE ATTENDANCE
# ==========================================

now = datetime.now()

date = now.strftime(
    "%Y-%m-%d"
)

time = now.strftime(
    "%H:%M:%S"
)


filename = (
    f"attendance_{date}.json"
)


filepath = os.path.join(
    ATTENDANCE_DIR,
    filename
)


attendance_data = {

    "date": date,

    "time": time,

    "attendance": attendance

}


with open(
    filepath,
    "w"
) as file:

    json.dump(
        attendance_data,
        file,
        indent=4
    )


print()
print(
    "Attendance saved successfully."
)

print(
    f"File: {filepath}"
)