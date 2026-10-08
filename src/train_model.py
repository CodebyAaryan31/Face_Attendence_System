import cv2
import os
import json


# ============================================================
# SETTINGS
# ============================================================

STUDENT_DIR = os.path.join(
    "data",
    "students"
)

ENCODING_DIR = os.path.join(
    "data",
    "encodings"
)

MODEL_PATH = os.path.join(
    ENCODING_DIR,
    "trainer.yml"
)

LABEL_PATH = os.path.join(
    ENCODING_DIR,
    "labels.json"
)


# ============================================================
# TRAIN MODEL
# ============================================================

def train_model():

    print()
    print("=" * 50)
    print("FACE RECOGNITION TRAINING")
    print("=" * 50)
    print()

    # --------------------------------------------------------
    # Check student directory
    # --------------------------------------------------------

    if not os.path.exists(STUDENT_DIR):

        print("Student directory does not exist.")

        return

    # --------------------------------------------------------
    # Create encoding directory
    # --------------------------------------------------------

    os.makedirs(
        ENCODING_DIR,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Load face detector
    # --------------------------------------------------------

    face_detector = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )

    if face_detector.empty():

        print("Could not load face detector.")

        return

    # --------------------------------------------------------
    # Create LBPH recognizer
    # --------------------------------------------------------

    recognizer = cv2.face.LBPHFaceRecognizer_create()

    # --------------------------------------------------------
    # Storage
    # --------------------------------------------------------

    faces = []

    labels = []

    label_names = {}

    current_label = 0

    # ========================================================
    # READ STUDENT FOLDERS
    # ========================================================

    student_names = sorted(
        os.listdir(STUDENT_DIR)
    )

    for student_name in student_names:

        student_path = os.path.join(
            STUDENT_DIR,
            student_name
        )

        # Ignore files
        if not os.path.isdir(student_path):
            continue

        current_label += 1

        label_names[str(current_label)] = student_name

        print(
            f"\nStudent: {student_name}"
        )

        # ----------------------------------------------------
        # Read student's photos
        # ----------------------------------------------------

        image_files = sorted(
            os.listdir(student_path)
        )

        student_photo_count = 0

        for image_file in image_files:

            image_path = os.path.join(
                student_path,
                image_file
            )

            # ------------------------------------------------
            # Read image
            # ------------------------------------------------

            image = cv2.imread(
                image_path
            )

            if image is None:

                print(
                    f"Could not read: {image_file}"
                )

                continue

            # ------------------------------------------------
            # Convert to grayscale
            # ------------------------------------------------

            gray = cv2.cvtColor(
                image,
                cv2.COLOR_BGR2GRAY
            )

            # ------------------------------------------------
            # Detect face again
            # ------------------------------------------------

            detected_faces = face_detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(80, 80)
            )

            if len(detected_faces) == 0:

                print(
                    f"  No face found: {image_file}"
                )

                continue

            # ------------------------------------------------
            # Use the largest detected face
            # ------------------------------------------------

            largest_face = max(
                detected_faces,
                key=lambda rectangle:
                    rectangle[2] * rectangle[3]
            )

            x, y, w, h = largest_face

            face = gray[
                y:y + h,
                x:x + w
            ]

            # ------------------------------------------------
            # Store training data
            # ------------------------------------------------

            faces.append(face)

            labels.append(current_label)

            student_photo_count += 1

            print(
                f"  Added: {image_file}"
            )

        print(
            f"  Usable photos: {student_photo_count}"
        )

    # ========================================================
    # CHECK TRAINING DATA
    # ========================================================

    if len(faces) == 0:

        print()
        print("No usable face images found.")

        return

    # ========================================================
    # TRAIN
    # ========================================================

    print()
    print(
        f"Training model with {len(faces)} face images..."
    )

    recognizer.train(
        faces,
        __import__("numpy").array(labels)
    )

    # ========================================================
    # SAVE MODEL
    # ========================================================

    recognizer.write(
        MODEL_PATH
    )

    # ========================================================
    # SAVE LABELS
    # ========================================================

    with open(
        LABEL_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            label_names,
            file,
            indent=4
        )

    # ========================================================
    # RESULT
    # ========================================================

    print()
    print("=" * 50)
    print("TRAINING COMPLETED SUCCESSFULLY")
    print("=" * 50)
    print()

    print(
        f"Students trained: {len(label_names)}"
    )

    print(
        f"Face images used: {len(faces)}"
    )

    print()
    print(
        f"Model saved to: {MODEL_PATH}"
    )

    print(
        f"Labels saved to: {LABEL_PATH}"
    )

    print()


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    train_model()