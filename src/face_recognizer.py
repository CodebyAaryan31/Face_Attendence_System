import cv2
import os
import json


# -----------------------------
# File paths
# -----------------------------

MODEL_PATH = os.path.join("data", "encodings", "trainer.yml")
LABEL_PATH = os.path.join("data", "encodings", "labels.json")


# -----------------------------
# Check required files
# -----------------------------

if not os.path.exists(MODEL_PATH):
    print("ERROR: trainer.yml not found.")
    print("Run train_model.py first.")
    exit()

if not os.path.exists(LABEL_PATH):
    print("ERROR: labels.json not found.")
    print("Run train_model.py first.")
    exit()


# -----------------------------
# Load face detector
# -----------------------------

cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

face_detector = cv2.CascadeClassifier(cascade_path)


# -----------------------------
# Load LBPH model
# -----------------------------

recognizer = cv2.face.LBPHFaceRecognizer_create()

recognizer.read(MODEL_PATH)


# -----------------------------
# Load student labels
# -----------------------------

with open(LABEL_PATH, "r") as file:
    labels = json.load(file)


# -----------------------------
# Start camera
# -----------------------------

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Could not open camera.")
    exit()


print("\n===================================")
print("   MULTI-FACE RECOGNITION")
print("===================================")
print("Press Q to quit.")


while True:

    ret, frame = camera.read()

    if not ret:
        print("ERROR: Could not read camera.")
        break

    # Mirror camera
    frame = cv2.flip(frame, 1)

    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect all faces
    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80)
    )


    # --------------------------------
    # Recognize every detected face
    # --------------------------------

    recognized_people = set()

    for (x, y, w, h) in faces:

        # Crop face
        face = gray[y:y + h, x:x + w]

        # Resize to training size
        face = cv2.resize(face, (200, 200))

        # Predict
        label, confidence = recognizer.predict(face)


        # --------------------------------
        # Check recognition confidence
        # --------------------------------

        if confidence < 70:

            name = labels.get(str(label), "Unknown")

            box_color = (0, 255, 0)

            recognized_people.add(name)

        else:

            name = "Unknown"

            box_color = (0, 0, 255)


        # --------------------------------
        # Draw face rectangle
        # --------------------------------

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            box_color,
            2
        )


        # --------------------------------
        # Display name
        # --------------------------------

        cv2.putText(
            frame,
            name,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            box_color,
            2
        )


        # --------------------------------
        # Display confidence
        # --------------------------------

        cv2.putText(
            frame,
            f"{confidence:.1f}",
            (x, y + h + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            box_color,
            2
        )


    # --------------------------------
    # Display statistics
    # --------------------------------

    cv2.putText(
        frame,
        f"Faces Detected: {len(faces)}",
        (20, 35),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )


    cv2.putText(
        frame,
        f"Recognized: {len(recognized_people)}",
        (20, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )


    # --------------------------------
    # Display camera
    # --------------------------------

    cv2.imshow(
        "Multi-Face Recognition",
        frame
    )


    # --------------------------------
    # Quit
    # --------------------------------

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# -----------------------------
# Cleanup
# -----------------------------

camera.release()

cv2.destroyAllWindows()


print("\nRecognition stopped.")

print("\nRecognized people:")

for person in recognized_people:
    print("-", person)