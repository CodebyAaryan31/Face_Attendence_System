import cv2
import os
import re


# Number of photos we want for each student
TOTAL_PHOTOS = 10


def clean_name(name):
    """
    Convert a student's name into a safe folder name.
    Example:
    'Aaryan Patidar' -> 'Aaryan_Patidar'
    """

    name = name.strip()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^a-zA-Z0-9_]", "", name)

    return name


def register_student():
    # Ask for student's name
    name = input("Enter student name: ").strip()

    if not name:
        print("Student name cannot be empty.")
        return

    # Convert name into a safe folder name
    student_name = clean_name(name)

    if not student_name:
        print("Invalid student name.")
        return

    # Create student folder
    student_folder = os.path.join(
        "data",
        "students",
        student_name
    )

    os.makedirs(student_folder, exist_ok=True)

    print()
    print(f"Registering: {name}")
    print(f"Photos will be saved in: {student_folder}")
    print()

    # Load OpenCV's built-in face detector
    face_detector = cv2.CascadeClassifier(
        cv2.data.haarcascades +
        "haarcascade_frontalface_default.xml"
    )

    # Open camera
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Could not open camera.")
        return

    photo_count = 0

    print("Camera started.")
    print()
    print("Instructions:")
    print("SPACE → Capture photo")
    print("Q     → Cancel registration")
    print()

    while True:
        success, frame = camera.read()

        if not success:
            print("Could not read camera frame.")
            break

        # Mirror the camera preview
        frame = cv2.flip(frame, 1)

        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )

        # Draw rectangle around every detected face
        for (x, y, w, h) in faces:

            if len(faces) == 1:
                color = (0, 255, 0)
            else:
                color = (0, 0, 255)

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                color,
                2
            )

        # Display information
        cv2.putText(
            frame,
            f"Photos: {photo_count}/{TOTAL_PHOTOS}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        if len(faces) == 0:

            cv2.putText(
                frame,
                "No face detected",
                (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

        elif len(faces) > 1:

            cv2.putText(
                frame,
                "Only one face should be visible",
                (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

        else:

            cv2.putText(
                frame,
                "Face detected - Press SPACE",
                (20, 75),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

        # Show camera
        cv2.imshow("Student Registration", frame)

        key = cv2.waitKey(1) & 0xFF

        # SPACE → capture
        if key == ord(" "):

            if len(faces) == 1:

                x, y, w, h = faces[0]

                # Add a small margin around the face
                margin = 20

                x1 = max(0, x - margin)
                y1 = max(0, y - margin)

                x2 = min(frame.shape[1], x + w + margin)
                y2 = min(frame.shape[0], y + h + margin)

                face_image = frame[y1:y2, x1:x2]

                photo_count += 1

                filename = os.path.join(
                    student_folder,
                    f"face_{photo_count}.jpg"
                )

                cv2.imwrite(filename, face_image)

                print(
                    f"Photo {photo_count}/{TOTAL_PHOTOS} saved."
                )

                # Stop after required number of photos
                if photo_count >= TOTAL_PHOTOS:

                    print()
                    print("Registration completed successfully!")
                    break

            else:

                print(
                    "Photo not captured. "
                    "Make sure exactly one face is visible."
                )

        # Q → quit
        elif key == ord("q"):

            print()
            print("Registration cancelled.")
            break

    # Release camera
    camera.release()

    # Close OpenCV windows
    cv2.destroyAllWindows()


if __name__ == "__main__":
    register_student()