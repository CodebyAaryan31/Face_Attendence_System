import cv2

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Could not open camera.")
    exit()

print("Camera started.")
print("Press Q inside the camera window to quit.")

while True:
    success, frame = camera.read()

    if not success:
        print("Could not read frame from camera.")
        break

    # Mirror the camera preview
    frame = cv2.flip(frame, 1)

    cv2.imshow("Camera Test", frame)

    # Press Q to close
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()

print("Camera closed.")