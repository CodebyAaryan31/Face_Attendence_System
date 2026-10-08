import cv2


# -----------------------------
# Load Haar Cascade
# -----------------------------

cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

face_detector = cv2.CascadeClassifier(cascade_path)


# -----------------------------
# Start camera
# -----------------------------

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Could not open camera.")
    exit()


print("\nMultiple Face Detection Started")
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

    # Detect ALL faces
    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80)
    )

    # Draw every detected face
    for index, (x, y, w, h) in enumerate(faces):

        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Face {index + 1}",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    # Display total number of faces
    cv2.putText(
        frame,
        f"Faces Detected: {len(faces)}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.9,
        (255, 255, 255),
        2
    )

    # Show camera
    cv2.imshow("Multiple Face Detection", frame)

    # Quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# -----------------------------
# Cleanup
# -----------------------------

camera.release()
cv2.destroyAllWindows()

print("Multiple Face Detection Stopped.")