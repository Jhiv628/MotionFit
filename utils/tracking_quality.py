def get_required_bicep_landmarks(pose_detector, arm_side):
    """
    Returns the key landmarks required to analyse a bicep curl.

    For a bicep curl, we need:
    - Shoulder
    - Elbow
    - Wrist
    - Hip

    If any of these are hidden or poorly visible, the form score becomes unreliable.
    """

    mp_pose = pose_detector.mp_pose

    if arm_side == "left":
        return [
            ("Left shoulder", mp_pose.PoseLandmark.LEFT_SHOULDER),
            ("Left elbow", mp_pose.PoseLandmark.LEFT_ELBOW),
            ("Left wrist", mp_pose.PoseLandmark.LEFT_WRIST),
            ("Left hip", mp_pose.PoseLandmark.LEFT_HIP),
        ]

    return [
        ("Right shoulder", mp_pose.PoseLandmark.RIGHT_SHOULDER),
        ("Right elbow", mp_pose.PoseLandmark.RIGHT_ELBOW),
        ("Right wrist", mp_pose.PoseLandmark.RIGHT_WRIST),
        ("Right hip", mp_pose.PoseLandmark.RIGHT_HIP),
    ]


def is_point_inside_frame(point):
    """
    Checks whether a landmark is inside the camera frame.

    MediaPipe points are normalised:
    x = 0 means far left of screen
    x = 1 means far right of screen
    y = 0 means top of screen
    y = 1 means bottom of screen
    """

    x, y = point

    return 0 <= x <= 1 and 0 <= y <= 1


def calculate_arm_visibility_score(landmarks, pose_detector, arm_side):
    """
    Calculates average visibility for the selected arm.

    MediaPipe gives every landmark a visibility score.
    Higher visibility means MediaPipe is more confident that the body point is visible.
    """

    required_landmarks = get_required_bicep_landmarks(pose_detector, arm_side)

    visibility_scores = []

    for _, landmark in required_landmarks:
        visibility = pose_detector.get_visibility(landmarks, landmark)
        visibility_scores.append(visibility)

    return sum(visibility_scores) / len(visibility_scores)


def choose_best_tracking_arm(landmarks, pose_detector):
    """
    Chooses the arm with better tracking visibility.

    This is important because if the user turns sideways,
    one arm may become hidden while the other is more visible.
    """

    left_score = calculate_arm_visibility_score(
        landmarks,
        pose_detector,
        "left"
    )

    right_score = calculate_arm_visibility_score(
        landmarks,
        pose_detector,
        "right"
    )

    if left_score >= right_score:
        return "left", left_score

    return "right", right_score


def get_bicep_tracking_quality(landmarks, pose_detector, preferred_arm=None):
    """
    Checks whether the bicep curl can be analysed safely.

    This function prevents the app from giving bad scores when the body is not
    clearly visible. It returns:
    - whether tracking is ready
    - which arm should be analysed
    - a tracking score
    - feedback messages for the user
    """

    best_arm, best_score = choose_best_tracking_arm(landmarks, pose_detector)

    selected_arm = best_arm

    if preferred_arm in ["left", "right"]:
        preferred_score = calculate_arm_visibility_score(
            landmarks,
            pose_detector,
            preferred_arm
        )

        # Keep the previous arm if it is still reasonably visible.
        # Switch arms only if the other arm is clearly better.
        if preferred_score >= 0.60 or best_score < preferred_score + 0.15:
            selected_arm = preferred_arm

    required_landmarks = get_required_bicep_landmarks(
        pose_detector,
        selected_arm
    )

    messages = []
    visibility_scores = []
    inside_frame_count = 0

    visibility_threshold = 0.60

    for label, landmark in required_landmarks:
        visibility = pose_detector.get_visibility(landmarks, landmark)
        point = pose_detector.get_point(landmarks, landmark)

        visibility_scores.append(visibility)

        if is_point_inside_frame(point):
            inside_frame_count += 1
        else:
            messages.append(f"{label} is outside the camera frame")

        if visibility < visibility_threshold:
            messages.append(f"{label} is not clearly visible")

    average_visibility = sum(visibility_scores) / len(visibility_scores)
    frame_score = inside_frame_count / len(required_landmarks)

    tracking_score = int(((average_visibility * 0.8) + (frame_score * 0.2)) * 100)

    if tracking_score < 65:
        messages.insert(0, "Move back and show your full working arm")

    if len(messages) == 0 and tracking_score < 80:
        messages.append("Tracking is weak - turn slightly towards the camera")

    tracking_ready = tracking_score >= 65 and len(messages) == 0

    return {
        "tracking_ready": tracking_ready,
        "selected_arm": selected_arm,
        "tracking_score": tracking_score,
        "messages": messages[:4],
    }