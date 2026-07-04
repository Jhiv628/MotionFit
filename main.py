import cv2

from utils.pose_detector import PoseDetector
from exercises.bicep_curl import BicepCurlAnalyzer


WINDOW_NAME = "MotionFit - Upper Body Tracker"
FULLSCREEN_MODE = True


def get_score_color(score):
    """
    Returns a colour based on the form score.
    OpenCV uses BGR colour order, not RGB.
    """

    if score >= 80:
        return (0, 255, 0)      # Green
    elif score >= 50:
        return (0, 255, 255)    # Yellow

    return (0, 0, 255)          # Red


def get_screen_size():
    """
    Gets the user's monitor size using tkinter.
    If tkinter fails for any reason, it safely falls back to 1280x720.
    """

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
    """
    Resizes the camera frame so it fills the screen.
    This fixes the issue where the video appears small with grey space around it.
    """

    return cv2.resize(
        frame,
        (screen_width, screen_height),
        interpolation=cv2.INTER_LINEAR
    )


def draw_transparent_panel(frame, x, y, width, height, alpha=0.65):
    """
    Draws a dark transparent panel behind the dashboard.
    This makes the text readable even when the camera background is bright.
    """

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
    """
    Draws one dashboard row.
    Example:
    Good reps      3
    Bad reps       1
    """

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
    """
    Draws the full MotionFit dashboard on the camera feed.
    It displays reps, stage, elbow angle, form score, rep quality, and feedback.
    """

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

    # Form score section
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

    # Live feedback title
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

    # Only show the first 3 feedback messages so the UI stays clean
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
    """
    Shows a clean message when MediaPipe cannot detect a person.
    """

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
    """
    Main application loop.
    This opens the camera, detects the body pose, analyzes the bicep curl,
    draws the skeleton/dashboard, and shows everything in a full-screen window.
    """

    cap = cv2.VideoCapture(0)

    # Ask the webcam for a higher resolution.
    # The camera may not always give exactly 1280x720, but this improves quality if supported.
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

        # Mirror the camera so it feels natural, like looking in a mirror.
        frame = cv2.flip(frame, 1)

        # MediaPipe needs RGB, but OpenCV uses BGR.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect pose landmarks.
        results = pose_detector.detect_pose(rgb_frame)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # Analyze the bicep curl using the detected landmarks.
            analysis = bicep_curl.analyze(landmarks, pose_detector)

            # Draw full body skeleton.
            pose_detector.draw_full_body_joints(frame, results)

            # Label shoulders, elbows, and wrists.
            pose_detector.draw_upper_body_labels(frame, landmarks)

            # Highlight the active curling arm.
            pose_detector.draw_active_arm_highlight(
                frame,
                landmarks,
                bicep_curl.selected_arm
            )

            # Draw the app dashboard.
            draw_dashboard(frame, analysis)

        else:
            draw_no_body_detected(frame)

        # Resize the final frame so it fills your monitor.
        display_frame = resize_frame_to_screen(
            frame,
            screen_width,
            screen_height
        )

        cv2.imshow(WINDOW_NAME, display_frame)

        key = cv2.waitKey(10) & 0xFF

        # Q or Escape closes the app.
        if key == ord("q") or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()