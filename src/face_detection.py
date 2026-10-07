from pathlib import Path
import cv2
import mediapipe as mp

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


MODEL_PATH = str(Path(__file__).resolve().parent.parent / "face_landmarker.task")


base_options = python.BaseOptions(
    model_asset_path=MODEL_PATH
)

options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.IMAGE,
    num_faces=5
)

face_landmarker = vision.FaceLandmarker.create_from_options(options)


def detect_faces(frame):
    """
    Detect faces in a webcam frame.

    Returns:
        face_landmarks: detected face landmarks
        face_count: number of detected faces
    """

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    results = face_landmarker.detect(mp_image)

    face_landmarks = results.face_landmarks
    face_count = len(face_landmarks)

    return face_landmarks, face_count