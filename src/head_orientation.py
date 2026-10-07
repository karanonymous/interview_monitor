import math


def get_landmark_point(landmarks, index, image_width, image_height):
    """
    Convert a MediaPipe landmark into pixel coordinates.
    """

    landmark = landmarks[index]

    x = int(landmark.x * image_width)
    y = int(landmark.y * image_height)

    return x, y


def calculate_distance(point1, point2):
    """
    Calculate distance between two points.
    """

    x1, y1 = point1
    x2, y2 = point2

    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def estimate_head_direction(landmarks, image_width, image_height):
    """
    Estimate whether the person's head is facing
    forward, left, right, or downward.

    Returns:
        direction, confidence_value
    """

    # Important MediaPipe Face Mesh landmarks
    nose = get_landmark_point(
        landmarks, 1, image_width, image_height
    )

    left_eye = get_landmark_point(
        landmarks, 33, image_width, image_height
    )

    right_eye = get_landmark_point(
        landmarks, 263, image_width, image_height
    )

    chin = get_landmark_point(
        landmarks, 152, image_width, image_height
    )

    # --------------------------------------------------
    # Calculate face geometry
    # --------------------------------------------------

    eye_center_x = (left_eye[0] + right_eye[0]) / 2
    eye_center_y = (left_eye[1] + right_eye[1]) / 2

    eye_distance = calculate_distance(left_eye, right_eye)

    if eye_distance == 0:
        return "UNKNOWN", 0

    # --------------------------------------------------
    # Horizontal head movement
    # --------------------------------------------------

    horizontal_offset = (nose[0] - eye_center_x) / eye_distance

    # --------------------------------------------------
    # Vertical head movement
    # --------------------------------------------------

    vertical_offset = (nose[1] - eye_center_y) / eye_distance

    # --------------------------------------------------
    # Thresholds
    # --------------------------------------------------

    horizontal_threshold = 0.25
    downward_threshold = 0.55

    # Looking left/right
    if horizontal_offset < -horizontal_threshold:
        direction = "LEFT"

    elif horizontal_offset > horizontal_threshold:
        direction = "RIGHT"

    # Looking downward
    elif vertical_offset > downward_threshold:
        direction = "DOWN"

    else:
        direction = "FORWARD"

    return direction, abs(horizontal_offset)