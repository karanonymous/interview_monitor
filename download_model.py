import urllib.request
URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
print("Downloading face_landmarker.task ...")
urllib.request.urlretrieve(URL, "face_landmarker.task")
print("Done.")
