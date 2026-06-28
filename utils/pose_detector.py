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

    def draw_joint_label(self, frame, point, label, color=(255, 255, 255)):
        point_px = self.convert_to_pixel_coordinates(point, frame)

        cv2.circle(frame, point_px, 11, (0, 0, 0), -1)
        cv2.circle(frame, point_px, 7, color, -1)

        cv2.putText(
            frame,
            label,
            (point_px[0] + 10, point_px[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            color,
            2
        )

    def draw_upper_body_labels(self, frame, landmarks):
        joints_to_label = [
            {
                "landmark": self.mp_pose.PoseLandmark.LEFT_SHOULDER,
                "label": "L Shoulder",
                "color": (255, 255, 255)
            },
            {
                "landmark": self.mp_pose.PoseLandmark.LEFT_ELBOW,
                "label": "L Elbow",
                "color": (0, 255, 0)
            },
            {
                "landmark": self.mp_pose.PoseLandmark.LEFT_WRIST,
                "label": "L Wrist",
                "color": (255, 255, 255)
            },
            {
                "landmark": self.mp_pose.PoseLandmark.RIGHT_SHOULDER,
                "label": "R Shoulder",
                "color": (255, 255, 255)
            },
            {
                "landmark": self.mp_pose.PoseLandmark.RIGHT_ELBOW,
                "label": "R Elbow",
                "color": (0, 255, 0)
            },
            {
                "landmark": self.mp_pose.PoseLandmark.RIGHT_WRIST,
                "label": "R Wrist",
                "color": (255, 255, 255)
            }
        ]

        for joint in joints_to_label:
            visibility = self.get_visibility(landmarks, joint["landmark"])

            if visibility > 0.5:
                point = self.get_point(landmarks, joint["landmark"])

                self.draw_joint_label(
                    frame,
                    point,
                    joint["label"],
                    joint["color"]
                )

    def draw_active_arm_highlight(self, frame, landmarks, arm_side):
        shoulder, elbow, wrist = self.get_arm_points(landmarks, arm_side)

        shoulder_px = self.convert_to_pixel_coordinates(shoulder, frame)
        elbow_px = self.convert_to_pixel_coordinates(elbow, frame)
        wrist_px = self.convert_to_pixel_coordinates(wrist, frame)

        cv2.line(frame, shoulder_px, elbow_px, (0, 255, 255), 7)
        cv2.line(frame, elbow_px, wrist_px, (0, 255, 255), 7)

        cv2.circle(frame, shoulder_px, 13, (0, 0, 0), -1)
        cv2.circle(frame, elbow_px, 13, (0, 0, 0), -1)
        cv2.circle(frame, wrist_px, 13, (0, 0, 0), -1)

        cv2.circle(frame, shoulder_px, 9, (0, 255, 255), -1)
        cv2.circle(frame, elbow_px, 9, (0, 255, 0), -1)
        cv2.circle(frame, wrist_px, 9, (0, 255, 255), -1)