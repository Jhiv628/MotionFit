import cv2

from utils.pose_detector import PoseDetector
from utils.tracking_quality import get_bicep_tracking_quality
from exercises.bicep_curl import BicepCurlAnalyzer


WINDOW_NAME = "MotionFit - Upper Body Tracker"
FULLSCREEN_MODE = True


def get_score_color(score):
    if score >= 80:
        return (0, 255, 0)      # Green

    if score >= 50:
        return (0, 255, 255)    # Yellow

    return (0, 0, 255)          # Red


def get_screen_size():
    try:
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        root.destroy()

        return screen_width, screen_height

    except Exception:
        return 1280, 720


def resize_frame_to_screen(frame, screen_width, screen_height):
    return cv2.resize(
        frame,
        (screen_width, screen_height),
        interpolation=cv2.INTER_LINEAR
    )


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

    cv2.rectangle(
        frame,
        (x, y),
        (x + 250, y + 12),
        (70, 70, 70),
        -1
    )

    bar_width = int((score / 100) * 250)

    cv2.rectangle(
        frame,
        (x, y),
        (x + bar_width, y + 12),
        score_color,
        -1
    )

    y += 45

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


def draw_tracking_warning(frame, tracking):
    panel_x = 15
    panel_y = 15
    panel_w = 460
    panel_h = 205

    draw_transparent_panel(frame, panel_x, panel_y, panel_w, panel_h)

    x = panel_x + 18
    y = panel_y + 35

    cv2.putText(
        frame,
        "Tracking not ready",
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 255),
        2,
        cv2.LINE_AA
    )

    y += 35

    cv2.putText(
        frame,
        f"Tracking score: {tracking['tracking_score']}/100",
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )

    y += 35

    for message in tracking["messages"]:
        cv2.putText(
            frame,
            f"- {message}",
            (x, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (0, 255, 255),
            1,
            cv2.LINE_AA
        )

        y += 26


def draw_no_body_detected(frame):
    draw_transparent_panel(frame, 15, 15, 280, 75)

    cv2.putText(
        frame,
        "No body detected",
        (35, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA
    )


def main():
    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("Could not open webcam.")
        return

    screen_width, screen_height = get_screen_size()

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

    if FULLSCREEN_MODE:
        cv2.setWindowProperty(
            WINDOW_NAME,
            cv2.WND_PROP_FULLSCREEN,
            cv2.WINDOW_FULLSCREEN
        )

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

            tracking = get_bicep_tracking_quality(
                landmarks,
                pose_detector,
                bicep_curl.selected_arm
            )

            pose_detector.draw_full_body_joints(frame, results)

            # This simplified version only labels the selected/visible arm.
            # If your pose_detector.py does not support this yet,
            # temporarily change this back to:
            # pose_detector.draw_upper_body_labels(frame, landmarks)
            pose_detector.draw_upper_body_labels(
                frame,
                landmarks,
                tracking["selected_arm"]
            )

            if tracking["tracking_ready"]:
                bicep_curl.selected_arm = tracking["selected_arm"]

                analysis = bicep_curl.analyze(
                    landmarks,
                    pose_detector
                )

                pose_detector.draw_active_arm_highlight(
                    frame,
                    landmarks,
                    bicep_curl.selected_arm
                )

                draw_dashboard(frame, analysis)

            else:
                bicep_curl.reset_tracking_state()
                draw_tracking_warning(frame, tracking)

        else:
            bicep_curl.reset_tracking_state()
            draw_no_body_detected(frame)

        display_frame = resize_frame_to_screen(
            frame,
            screen_width,
            screen_height
        )

        cv2.imshow(WINDOW_NAME, display_frame)

        key = cv2.waitKey(10) & 0xFF

        if key == ord("q") or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()