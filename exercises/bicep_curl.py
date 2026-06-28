from utils.angles import calculate_angle, calculate_distance


class BicepCurlAnalyzer:
    def __init__(self):
        self.good_reps = 0
        self.bad_reps = 0
        self.stage = "waiting"

        self.selected_arm = None

        self.starting_elbow_position = None
        self.starting_shoulder_position = None

        self.rep_started = False
        self.reached_top = False
        self.fully_extended = False

        self.max_elbow_swing = 0
        self.max_shoulder_swing = 0
        self.min_elbow_angle = 180
        self.max_elbow_angle = 0

        self.last_rep_feedback = []
        self.current_rep_quality = "Waiting for full extension"

    def analyze(self, landmarks, pose_detector):
        if self.selected_arm is None:
            self.selected_arm = pose_detector.choose_visible_arm(landmarks)

        shoulder, elbow, wrist = pose_detector.get_arm_points(
            landmarks,
            self.selected_arm
        )

        hip = self.get_hip_point(landmarks, pose_detector)

        elbow_angle = calculate_angle(shoulder, elbow, wrist)
        shoulder_angle = calculate_angle(hip, shoulder, elbow)

        upper_arm_length = calculate_distance(shoulder, elbow)

        if upper_arm_length == 0:
            upper_arm_length = 0.001

        if elbow_angle > 155 and not self.rep_started:
            self.reset_rep_tracking(shoulder, elbow)

        elbow_swing = 0
        shoulder_swing = 0

        if self.starting_elbow_position is not None:
            elbow_swing = calculate_distance(elbow, self.starting_elbow_position)
            elbow_swing = elbow_swing / upper_arm_length

        if self.starting_shoulder_position is not None:
            shoulder_swing = calculate_distance(shoulder, self.starting_shoulder_position)
            shoulder_swing = shoulder_swing / upper_arm_length

        self.max_elbow_swing = max(self.max_elbow_swing, elbow_swing)
        self.max_shoulder_swing = max(self.max_shoulder_swing, shoulder_swing)
        self.min_elbow_angle = min(self.min_elbow_angle, elbow_angle)
        self.max_elbow_angle = max(self.max_elbow_angle, elbow_angle)

        feedback = self.get_live_feedback(
            elbow_angle,
            shoulder_angle,
            elbow_swing,
            shoulder_swing
        )

        form_score = self.calculate_form_score(
            elbow_angle,
            elbow_swing,
            shoulder_swing
        )

        self.update_rep_state(elbow_angle)

        return {
            "exercise": "Bicep Curl",
            "arm": self.selected_arm,
            "good_reps": self.good_reps,
            "bad_reps": self.bad_reps,
            "total_reps": self.good_reps + self.bad_reps,
            "stage": self.stage,
            "elbow_angle": elbow_angle,
            "shoulder_angle": shoulder_angle,
            "elbow_swing": elbow_swing,
            "shoulder_swing": shoulder_swing,
            "form_score": form_score,
            "current_rep_quality": self.current_rep_quality,
            "feedback": feedback,
            "last_rep_feedback": self.last_rep_feedback
        }

    def get_hip_point(self, landmarks, pose_detector):
        mp_pose = pose_detector.mp_pose

        if self.selected_arm == "left":
            return pose_detector.get_point(
                landmarks,
                mp_pose.PoseLandmark.LEFT_HIP
            )

        return pose_detector.get_point(
            landmarks,
            mp_pose.PoseLandmark.RIGHT_HIP
        )

    def reset_rep_tracking(self, shoulder, elbow):
        self.starting_elbow_position = elbow
        self.starting_shoulder_position = shoulder

        self.rep_started = True
        self.reached_top = False
        self.fully_extended = True

        self.max_elbow_swing = 0
        self.max_shoulder_swing = 0
        self.min_elbow_angle = 180
        self.max_elbow_angle = 0

        self.last_rep_feedback = []
        self.current_rep_quality = "Rep started"

    def update_rep_state(self, elbow_angle):
        if elbow_angle > 155:
            if self.stage == "up":
                self.finish_rep()

            self.stage = "down"
            self.fully_extended = True

        elif elbow_angle < 55:
            if self.stage == "down":
                self.stage = "up"
                self.reached_top = True

        elif 55 <= elbow_angle <= 155:
            if self.stage == "down":
                self.stage = "curling up"
            elif self.stage == "up":
                self.stage = "lowering"

    def finish_rep(self):
        rep_feedback = []

        if not self.reached_top:
            rep_feedback.append("Curl did not reach the top")

        if not self.fully_extended:
            rep_feedback.append("Arm did not fully extend")

        if self.max_elbow_swing > 0.45:
            rep_feedback.append("Too much elbow movement")

        if self.max_shoulder_swing > 0.25:
            rep_feedback.append("Shoulder moved too much")

        if self.min_elbow_angle > 65:
            rep_feedback.append("Curl range of motion too short")

        if self.max_elbow_angle < 145:
            rep_feedback.append("Arm was not extended enough")

        if len(rep_feedback) == 0:
            self.good_reps += 1
            self.current_rep_quality = "Good rep"
            self.last_rep_feedback = ["Good rep"]
        else:
            self.bad_reps += 1
            self.current_rep_quality = "Bad rep"
            self.last_rep_feedback = rep_feedback

        self.rep_started = False
        self.reached_top = False
        self.fully_extended = False

    def get_live_feedback(
        self,
        elbow_angle,
        shoulder_angle,
        elbow_swing,
        shoulder_swing
    ):
        feedback = []

        if elbow_angle > 155:
            feedback.append("Start position ready")

        if 90 < elbow_angle <= 155:
            feedback.append("Curl up with control")

        if 55 <= elbow_angle <= 90:
            feedback.append("Nearly at the top")

        if elbow_angle < 55:
            feedback.append("Good curl height")

        if elbow_swing > 0.45:
            feedback.append("Keep elbow still")

        if shoulder_swing > 0.25:
            feedback.append("Avoid shoulder swinging")

        if shoulder_angle > 45:
            feedback.append("Keep upper arm closer to body")

        if elbow_angle < 35:
            feedback.append("Do not over-curl")

        return feedback

    def calculate_form_score(self, elbow_angle, elbow_swing, shoulder_swing):
        score = 100

        if elbow_swing > 0.30:
            score -= 20

        if elbow_swing > 0.45:
            score -= 20

        if shoulder_swing > 0.20:
            score -= 15

        if shoulder_swing > 0.35:
            score -= 15

        if 65 < elbow_angle < 155:
            score -= 5

        if elbow_angle < 35:
            score -= 10

        if score < 0:
            score = 0

        return score