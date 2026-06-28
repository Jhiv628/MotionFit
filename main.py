import cv2

from utils.pose_detector import PoseDetector
from exercises.bicep_curl import BicepCurlAnalyzer


def draw_text(frame, text, x, y, size=0.7):
    cv2.putText(
        frame,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        size,
        (255, 255, 255),
        2
    )


def draw_feedback(frame, feedback):
    y = 230

    for message in feedback:
        cv2.putText(
            frame,
            message,
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )
        y += 35


def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Could not open webcam.")
        return

    pose_detector = PoseDetector()
    bicep_curl = BicepCurlAnalyzer()

    while True:
        success, frame = cap.read()

        if not success:
            print("Could not read webcam frame.")
            break

        frame = cv2.flip(frame, 1)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose_detector.detect_pose(rgb_frame)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            analysis = bicep_curl.analyze(landmarks, pose_detector)

            pose_detector.draw_full_body_joints(frame, results)

            pose_detector.draw_active_arm_highlight(
                frame,
                landmarks,
                bicep_curl.selected_arm
            )

            draw_text(frame, f"Exercise: {analysis['exercise']}", 20, 40)
            draw_text(frame, f"Arm: {analysis['arm']}", 20, 75)
            draw_text(frame, f"Reps: {analysis['reps']}", 20, 110, 0.9)
            draw_text(frame, f"Stage: {analysis['stage']}", 20, 150)
            draw_text(frame, f"Elbow angle: {int(analysis['elbow_angle'])}", 20, 185)

            draw_feedback(frame, analysis["feedback"])

        else:
            draw_text(frame, "No body detected", 20, 40)

        cv2.imshow("MotionFit - Upper Body Tracker", frame)

        key = cv2.waitKey(10) & 0xFF

        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()