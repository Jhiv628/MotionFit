from utils.angles import calculate_angle, calculate_distance


class BicepCurlAnalyzer:
    def __init__(self):
        self.reps = 0
        self.stage = None
        self.selected_arm = None
        self.starting_elbow_position = None

    def analyze(self, landmarks, pose_detector):
        """
        Analyzes bicep curl form.
        Returns data that main.py can display.
        """

        if self.selected_arm is None:
            self.selected_arm = pose_detector.choose_visible_arm(landmarks)

        shoulder, elbow, wrist = pose_detector.get_arm_points(
            landmarks,
            self.selected_arm
        )

        elbow_angle = calculate_angle(shoulder, elbow, wrist)

        if self.starting_elbow_position is None and elbow_angle > 150:
            self.starting_elbow_position = elbow

        elbow_movement = 0

        if self.starting_elbow_position is not None:
            elbow_movement = calculate_distance(elbow, self.starting_elbow_position)

        # Rep counting logic
        if elbow_angle > 150:
            if self.stage == "up":
                self.reps += 1

            self.stage = "down"
            self.starting_elbow_position = elbow

        if elbow_angle < 55 and self.stage == "down":
            self.stage = "up"

        feedback = self.get_feedback(elbow_angle, elbow_movement)

        return {
            "exercise": "Bicep Curl",
            "arm": self.selected_arm,
            "reps": self.reps,
            "stage": self.stage,
            "elbow_angle": elbow_angle,
            "elbow_movement": elbow_movement,
            "feedback": feedback
        }

    def get_feedback(self, elbow_angle, elbow_movement):
        feedback = []

        if elbow_angle > 160:
            feedback.append("Arm fully extended")

        if 70 < elbow_angle < 140:
            feedback.append("Keep curling")

        if elbow_angle < 55:
            feedback.append("Good curl height")

        if elbow_movement > 0.08:
            feedback.append("Keep elbow still - avoid swinging")

        if elbow_angle < 35:
            feedback.append("Do not over-curl too high")

        return feedback