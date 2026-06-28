import cv2

from utils.pose_detector import PoseDetector
from exercises.bicep_curl import BicepCurlAnalyzer


def get_score_color(score):
    if score >= 80:
        return (0, 255, 0)      # Green
    elif score >= 50:
        return (0, 255, 255)    # Yellow
    return (0, 0, 255)          # Red


def draw_transparent_panel(frame, x, y, width, height, alpha=0.65):
    overlay = frame.copy()

    cv2.rectangle(
        overlay,
        (x, y),
        (x + width, y + height),
        (20, 20, 20),
        -1
    )

    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)


def draw_label_value(frame, label, value, x, y, value_color=(255, 255, 255)):
    cv2.putText(
        frame,
        label,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.48,
        (180, 180, 180),
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        str(value),
        (x + 135, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        value_color,
        2,
        cv2.LINE_AA
    )


def draw_dashboard(frame, analysis):
    panel_x = 15
    panel_y = 15
    panel_w = 320
    panel_h = 425

    draw_transparent_panel(frame, panel_x, panel_y, panel_w, panel_h)

    x = panel_x + 18
    y = panel_y + 35

    # App title
    cv2.putText(
        frame,
        "MotionFit",
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.85,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    y += 35

    # Exercise name
    cv2.putText(
        frame,
        analysis["exercise"],
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (0, 255, 255),
        2,
        cv2.LINE_AA
    )

    y += 35

    draw_label_value(frame, "Active arm", analysis["arm"], x, y)
    y += 30

    draw_label_value(frame, "Good reps", analysis["good_reps"], x, y, (0, 255, 0))
    y += 30

    draw_label_value(frame, "Bad reps", analysis["bad_reps"], x, y, (0, 0, 255))
    y += 30

    draw_label_value(frame, "Total reps", analysis["total_reps"], x, y)
    y += 30

    draw_label_value(frame, "Stage", analysis["stage"], x, y, (0, 255, 255))
    y += 30

    draw_label_value(frame, "Elbow angle", f"{int(analysis['elbow_angle'])}°", x, y)
    y += 35

    # Form score
    score = analysis["form_score"]
    score_color = get_score_color(score)

    cv2.putText(
        frame,
        "Form score",
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (180, 180, 180),
        1,
        cv2.LINE_AA
    )

    cv2.putText(
        frame,
        f"{score}/100",
        (x + 140, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        score_color,
        2,
        cv2.LINE_AA
    )

    y += 18

    # Score bar background
    cv2.rectangle(
        frame,
        (x, y),
        (x + 250, y + 12),
        (70, 70, 70),
        -1
    )

    # Score bar fill
    bar_width = int((score / 100) * 250)

    cv2.rectangle(
        frame,
        (x, y),
        (x + bar_width, y + 12),
        score_color,
        -1
    )

    y += 45

    # Rep quality
    cv2.putText(
        frame,
        "Rep quality",
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (180, 180, 180),
        1,
        cv2.LINE_AA
    )

    y += 25

    cv2.putText(
        frame,
        analysis["current_rep_quality"],
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    y += 35

    # Live feedback
    cv2.putText(
        frame,
        "Live feedback",
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (180, 180, 180),
        1,
        cv2.LINE_AA
    )

    y += 25

    feedback = analysis["feedback"][:3]

    for message in feedback:
        cv2.putText(
            frame,
            f"- {message}",
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.47,
            (0, 255, 255),
            1,
            cv2.LINE_AA
        )

        y += 24


def draw_no_body_detected(frame):
    draw_transparent_panel(frame, 15, 15, 260, 70)

    cv2.putText(
        frame,
        "No body detected",
        (35, 58),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )


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

            pose_detector.draw_upper_body_labels(frame, landmarks)

            pose_detector.draw_active_arm_highlight(
                frame,
                landmarks,
                bicep_curl.selected_arm
            )

            draw_dashboard(frame, analysis)

        else:
            draw_no_body_detected(frame)

        cv2.imshow("MotionFit - Upper Body Tracker", frame)

        key = cv2.waitKey(10) & 0xFF

        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()