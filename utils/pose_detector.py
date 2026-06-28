import cv2
import mediapipe as mp


class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils

        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

    def detect_pose(self, image_rgb):
        return self.pose.process(image_rgb)

    def get_point(self, landmarks, landmark):
        point = landmarks[landmark.value]
        return [point.x, point.y]

    def get_visibility(self, landmarks, landmark):
        return landmarks[landmark.value].visibility

    def choose_visible_arm(self, landmarks):
        left_visibility = (
            self.get_visibility(landmarks, self.mp_pose.PoseLandmark.LEFT_SHOULDER)
            + self.get_visibility(landmarks, self.mp_pose.PoseLandmark.LEFT_ELBOW)
            + self.get_visibility(landmarks, self.mp_pose.PoseLandmark.LEFT_WRIST)
        )

        right_visibility = (
            self.get_visibility(landmarks, self.mp_pose.PoseLandmark.RIGHT_SHOULDER)
            + self.get_visibility(landmarks, self.mp_pose.PoseLandmark.RIGHT_ELBOW)
            + self.get_visibility(landmarks, self.mp_pose.PoseLandmark.RIGHT_WRIST)
        )

        if left_visibility > right_visibility:
            return "left"

        return "right"

    def get_arm_points(self, landmarks, arm_side):
        if arm_side == "left":
            shoulder = self.get_point(landmarks, self.mp_pose.PoseLandmark.LEFT_SHOULDER)
            elbow = self.get_point(landmarks, self.mp_pose.PoseLandmark.LEFT_ELBOW)
            wrist = self.get_point(landmarks, self.mp_pose.PoseLandmark.LEFT_WRIST)
        else:
            shoulder = self.get_point(landmarks, self.mp_pose.PoseLandmark.RIGHT_SHOULDER)
            elbow = self.get_point(landmarks, self.mp_pose.PoseLandmark.RIGHT_ELBOW)
            wrist = self.get_point(landmarks, self.mp_pose.PoseLandmark.RIGHT_WRIST)

        return shoulder, elbow, wrist

    def convert_to_pixel_coordinates(self, point, frame):
        height, width, _ = frame.shape

        x = int(point[0] * width)
        y = int(point[1] * height)

        return x, y

    def draw_full_body_joints(self, frame, results):
        """
        Draws the full pose skeleton, but cleaner and more professional
        than the default MediaPipe drawing.
        """

        if not results.pose_landmarks:
            return

        self.mp_drawing.draw_landmarks(
            frame,
            results.pose_landmarks,
            self.mp_pose.POSE_CONNECTIONS,
            self.mp_drawing.DrawingSpec(
                color=(255, 255, 255),
                thickness=3,
                circle_radius=3
            ),
            self.mp_drawing.DrawingSpec(
                color=(0, 0, 255),
                thickness=2,
                circle_radius=4
            )
        )

    def draw_active_arm_highlight(self, frame, landmarks, arm_side):
        """
        Highlights the arm being used for the bicep curl.
        This keeps the full skeleton but makes the working arm clearer.
        """

        shoulder, elbow, wrist = self.get_arm_points(landmarks, arm_side)

        shoulder_px = self.convert_to_pixel_coordinates(shoulder, frame)
        elbow_px = self.convert_to_pixel_coordinates(elbow, frame)
        wrist_px = self.convert_to_pixel_coordinates(wrist, frame)

        # Thicker highlighted arm lines
        cv2.line(frame, shoulder_px, elbow_px, (0, 255, 255), 7)
        cv2.line(frame, elbow_px, wrist_px, (0, 255, 255), 7)

        # Black outline circles
        cv2.circle(frame, shoulder_px, 13, (0, 0, 0), -1)
        cv2.circle(frame, elbow_px, 13, (0, 0, 0), -1)
        cv2.circle(frame, wrist_px, 13, (0, 0, 0), -1)

        # Main joint circles
        cv2.circle(frame, shoulder_px, 9, (0, 255, 255), -1)
        cv2.circle(frame, elbow_px, 9, (0, 255, 0), -1)
        cv2.circle(frame, wrist_px, 9, (0, 255, 255), -1)

        # Labels for important curl joints only
        cv2.putText(
            frame,
            "Shoulder",
            (shoulder_px[0] + 10, shoulder_px[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "Elbow",
            (elbow_px[0] + 10, elbow_px[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            "Wrist",
            (wrist_px[0] + 10, wrist_px[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2
        )