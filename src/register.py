import cv2
import os
import re
import time


# ============================================================
# SETTINGS
# ============================================================

TOTAL_PHOTOS = 10

# Minimum face width and height
MIN_FACE_SIZE = 120

# Minimum sharpness score
# Higher = clearer image required
MIN_SHARPNESS = 80

# Minimum time between captures
CAPTURE_COOLDOWN = 0.8


# ============================================================
# NAME CLEANING
# ============================================================

def clean_name(name):
    """
    Convert a student's name into a safe folder name.

    Example:
        Aaryan Patidar
        ->
        Aaryan_Patidar
    """

    name = name.strip()

    # Replace multiple spaces with one underscore
    name = re.sub(r"\s+", "_", name)

    # Remove special characters
    name = re.sub(r"[^a-zA-Z0-9_]", "", name)

    return name


# ============================================================
# BLUR / SHARPNESS CHECK
# ============================================================

def calculate_sharpness(image):
    """
    Calculate image sharpness using Laplacian variance.

    Higher value = sharper image.
    Lower value = blurrier image.
    """

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    return cv2.Laplacian(gray, cv2.CV_64F).var()


# ============================================================
# REGISTER STUDENT
# ============================================================

def register_student():

    # --------------------------------------------------------
    # Ask for student name
    # --------------------------------------------------------

    name = input("Enter student name: ").strip()

    if not name:
        print("Student name cannot be empty.")
        return

    student_name = clean_name(name)

    if not student_name:
        print("Invalid student name.")
        return

    # --------------------------------------------------------
    # Create student folder
    # --------------------------------------------------------

    student_folder = os.path.join(
        "data",
        "students",
        student_name
    )

    os.makedirs(student_folder, exist_ok=True)

    print()
    print("=" * 50)
    print(f"Registering student: {name}")
    print(f"Saving photos to: {student_folder}")
    print("=" * 50)
    print()

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
    # Open camera
    # --------------------------------------------------------

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Could not open camera.")
        return

    # --------------------------------------------------------
    # Registration variables
    # --------------------------------------------------------

    photo_count = 0

    last_capture_time = 0

    print("Camera started.")
    print()
    print("Controls:")
    print("SPACE → Capture photo")
    print("Q     → Cancel registration")
    print()

    # ========================================================
    # CAMERA LOOP
    # ========================================================

    while True:

        success, frame = camera.read()

        if not success:
            print("Could not read camera frame.")
            break

        # Mirror camera preview
        frame = cv2.flip(frame, 1)

        # ----------------------------------------------------
        # Convert to grayscale
        # ----------------------------------------------------

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        # ----------------------------------------------------
        # Detect faces
        # ----------------------------------------------------

        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(MIN_FACE_SIZE, MIN_FACE_SIZE)
        )

        # ----------------------------------------------------
        # Status variables
        # ----------------------------------------------------

        status = ""
        status_color = (0, 0, 255)

        # ====================================================
        # NO FACE
        # ====================================================

        if len(faces) == 0:

            status = "No face detected"
            status_color = (0, 0, 255)

        # ====================================================
        # MULTIPLE FACES
        # ====================================================

        elif len(faces) > 1:

            status = "Only one face should be visible"
            status_color = (0, 0, 255)

            # Draw all detected faces
            for (x, y, w, h) in faces:

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 0, 255),
                    2
                )

        # ====================================================
        # EXACTLY ONE FACE
        # ====================================================

        else:

            x, y, w, h = faces[0]

            # ------------------------------------------------
            # Draw face rectangle
            # ------------------------------------------------

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            # ------------------------------------------------
            # Check face size
            # ------------------------------------------------

            if w < MIN_FACE_SIZE or h < MIN_FACE_SIZE:

                status = "Move closer to the camera"
                status_color = (0, 0, 255)

            else:

                # ------------------------------------------------
                # Crop face
                # ------------------------------------------------

                margin = 20

                x1 = max(0, x - margin)
                y1 = max(0, y - margin)

                x2 = min(
                    frame.shape[1],
                    x + w + margin
                )

                y2 = min(
                    frame.shape[0],
                    y + h + margin
                )

                face_image = frame[y1:y2, x1:x2]

                # ------------------------------------------------
                # Calculate sharpness
                # ------------------------------------------------

                sharpness = calculate_sharpness(face_image)

                # ------------------------------------------------
                # Check blur
                # ------------------------------------------------

                if sharpness < MIN_SHARPNESS:

                    status = "Image blurry - hold still"
                    status_color = (0, 0, 255)

                else:

                    status = "Good image - Press SPACE"
                    status_color = (0, 255, 0)

        # ====================================================
        # DISPLAY PHOTO COUNT
        # ====================================================

        cv2.putText(
            frame,
            f"Photos: {photo_count}/{TOTAL_PHOTOS}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        # ====================================================
        # DISPLAY STATUS
        # ====================================================

        cv2.putText(
            frame,
            status,
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            status_color,
            2
        )

        # ====================================================
        # DISPLAY INSTRUCTIONS
        # ====================================================

        cv2.putText(
            frame,
            "SPACE = Capture | Q = Quit",
            (20, frame.shape[0] - 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            2
        )

        # ====================================================
        # SHOW CAMERA
        # ====================================================

        cv2.imshow(
            "Student Registration",
            frame
        )

        # ====================================================
        # KEYBOARD INPUT
        # ====================================================

        key = cv2.waitKey(1) & 0xFF

        # ----------------------------------------------------
        # SPACE → Capture
        # ----------------------------------------------------

        if key == ord(" "):

            current_time = time.time()

            # Prevent accidental rapid captures
            if current_time - last_capture_time < CAPTURE_COOLDOWN:
                continue

            # Only capture when exactly one face exists
            if len(faces) != 1:

                print(
                    "Photo not captured. "
                    "Make sure exactly one face is visible."
                )

                continue

            # Get face coordinates
            x, y, w, h = faces[0]

            # Check face size
            if w < MIN_FACE_SIZE or h < MIN_FACE_SIZE:

                print(
                    "Photo not captured. "
                    "Move closer to the camera."
                )

                continue

            # ------------------------------------------------
            # Crop face
            # ------------------------------------------------

            margin = 20

            x1 = max(0, x - margin)
            y1 = max(0, y - margin)

            x2 = min(
                frame.shape[1],
                x + w + margin
            )

            y2 = min(
                frame.shape[0],
                y + h + margin
            )

            face_image = frame[y1:y2, x1:x2]

            # ------------------------------------------------
            # Check image sharpness
            # ------------------------------------------------

            sharpness = calculate_sharpness(face_image)

            if sharpness < MIN_SHARPNESS:

                print(
                    f"Photo not captured. "
                    f"Image is blurry ({sharpness:.1f})."
                )

                continue

            # ------------------------------------------------
            # Save photo
            # ------------------------------------------------

            photo_count += 1

            filename = os.path.join(
                student_folder,
                f"face_{photo_count}.jpg"
            )

            cv2.imwrite(
                filename,
                face_image
            )

            last_capture_time = current_time

            print(
                f"Photo {photo_count}/{TOTAL_PHOTOS} saved "
                f"(sharpness: {sharpness:.1f})"
            )

            # ------------------------------------------------
            # Registration complete
            # ------------------------------------------------

            if photo_count >= TOTAL_PHOTOS:

                print()
                print("=" * 50)
                print("Registration completed successfully!")
                print("=" * 50)
                print()

                break

        # ----------------------------------------------------
        # Q → Quit
        # ----------------------------------------------------

        elif key == ord("q"):

            print()
            print("Registration cancelled.")
            break

    # ========================================================
    # CLEANUP
    # ========================================================

    camera.release()

    cv2.destroyAllWindows()


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":
    register_student()