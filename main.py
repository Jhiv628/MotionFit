import cv2

from utils.pose_detector import PoseDetector
from utils.tracking_quality import get_bicep_tracking_quality
from exercises.bicep_curl import BicepCurlAnalyzer


def get_score_color(score):
<<<<<<< Updated upstream
=======
    """
    Returns a colour based on the user's form score.
    OpenCV uses BGR colour order, not RGB.
    """

>>>>>>> Stashed changes
    if score >= 80:
        return (0, 255, 0)      # Green

    if score >= 50:
        return (0, 255, 255)    # Yellow
    return (0, 0, 255)          # Red


<<<<<<< Updated upstream
def draw_transparent_panel(frame, x, y, width, height, alpha=0.65):
=======
def get_screen_size():
    """
    Gets the user's monitor size.

    This is used so the camera feed can be resized to fill the screen.
    If the screen size cannot be detected, it falls back to 1280x720.
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
    Resizes the camera frame to fit the monitor.

    This fixes the grey empty space issue where the OpenCV window is larger
    than the actual camera image.
    """

    return cv2.resize(
        frame,
        (screen_width, screen_height),
        interpolation=cv2.INTER_LINEAR
    )


def draw_transparent_panel(frame, x, y, width, height, alpha=0.65):
    """
    Draws a dark transparent panel.

    This makes dashboard text easier to read on top of the camera feed.
    """

>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
=======
    """
    Draws one dashboard row.

    Example:
    Good reps      3
    Bad reps       1
    """

>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
=======
    """
    Draws the main MotionFit dashboard.

    It shows:
    - exercise name
    - active arm
    - good reps
    - bad reps
    - total reps
    - stage
    - elbow angle
    - form score
    - rep quality
    - live feedback
    """

>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
    # Form score
=======
>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
    # Live feedback
=======
>>>>>>> Stashed changes
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
    """
    Draws a warning panel when the app cannot safely analyse the exercise.

    This prevents the app from giving bad form scores when the shoulder,
    elbow, wrist, or hip are not clearly visible.
    """

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
<<<<<<< Updated upstream
    draw_transparent_panel(frame, 15, 15, 260, 70)
=======
    """
    Draws a message when MediaPipe cannot detect a body at all.
    """

    draw_transparent_panel(frame, 15, 15, 280, 75)
>>>>>>> Stashed changes

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
<<<<<<< Updated upstream
    cap = cv2.VideoCapture(0)

=======
    """
    Main application loop.

    This function:
    - opens the webcam
    - detects body landmarks
    - checks tracking quality
    - analyses bicep curl form if tracking is good
    - pauses scoring if tracking is poor
    - draws the dashboard and skeleton
    """

    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
=======

>>>>>>> Stashed changes
        results = pose_detector.detect_pose(rgb_frame)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

<<<<<<< Updated upstream
            analysis = bicep_curl.analyze(landmarks, pose_detector)

            pose_detector.draw_full_body_joints(frame, results)

            pose_detector.draw_upper_body_labels(frame, landmarks)

            pose_detector.draw_active_arm_highlight(
                frame,
=======
            tracking = get_bicep_tracking_quality(
>>>>>>> Stashed changes
                landmarks,
                pose_detector,
                bicep_curl.selected_arm
            )

<<<<<<< Updated upstream
            draw_dashboard(frame, analysis)
=======
            pose_detector.draw_full_body_joints(frame, results)

            pose_detector.draw_upper_body_labels(frame, landmarks)

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
>>>>>>> Stashed changes

        else:
            bicep_curl.reset_tracking_state()
            draw_no_body_detected(frame)

<<<<<<< Updated upstream
        cv2.imshow("MotionFit - Upper Body Tracker", frame)

        key = cv2.waitKey(10) & 0xFF

        if key == ord("q"):
=======
        display_frame = resize_frame_to_screen(
            frame,
            screen_width,
            screen_height
        )

        cv2.imshow(WINDOW_NAME, display_frame)

        key = cv2.waitKey(10) & 0xFF

        if key == ord("q") or key == 27:
>>>>>>> Stashed changes
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()