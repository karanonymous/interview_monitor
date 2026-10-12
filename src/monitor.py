import threading, time
from pathlib import Path
import cv2
from event_logger import EventLogger
from screenshot_manager import ScreenshotManager

ROOT = Path(__file__).resolve().parent.parent


class Monitor:
    """Background thread: webcam -> face detection -> head direction -> anomalies."""

    def __init__(self, camera_index=0, hold_seconds=2.0):
        self.camera_index = camera_index
        self.hold = hold_seconds  # anomaly must persist this long to count
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.thread = None
        self.jpeg = None
        self.status = {"camera_status": "STARTING", "face_count": 0,
                       "head_direction": "N/A", "system_status": "STARTING"}
        self.logger = EventLogger(ROOT / "logs" / "interview_events.csv")
        self.shots = ScreenshotManager(str(ROOT / "screenshots"))

    def start(self):
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread and self.thread is not threading.current_thread():
            self.thread.join(timeout=5)
            if self.thread.is_alive():
                print("[MONITOR ERROR] Webcam thread did not stop within 5 seconds")

    def get_status(self):
        with self.lock:
            return dict(self.status)

    def get_jpeg(self):
        with self.lock:
            return self.jpeg

    def _set(self, **kw):
        with self.lock:
            self.status.update(kw)

    def _run(self):
        try:
            from face_detection import detect_faces
            from head_orientation import estimate_head_direction
        except Exception as e:  # missing package or face_landmarker.task
            self._set(camera_status="OFFLINE", system_status=f"ERROR: {e}")
            print(f"[MONITOR ERROR] {e}")
            return
        cap = cv2.VideoCapture(self.camera_index)
        if not cap.isOpened():
            self._set(camera_status="OFFLINE", system_status="ERROR: cannot open webcam")
            return

        since, active = {}, set()
        try:
            while not self.stop_event.is_set():
                ok, frame = cap.read()
                if not ok:
                    self._set(camera_status="OFFLINE")
                    time.sleep(0.2)
                    continue

                frame = cv2.flip(frame, 1)
                faces, count = detect_faces(frame)
                direction, anomaly, details = "N/A", None, ""
                if count == 0:
                    anomaly, details = "NO_FACE", "No face detected"
                elif count > 1:
                    anomaly, details = "MULTIPLE_FACES", f"{count} faces detected"
                else:
                    h, w = frame.shape[:2]
                    direction, _ = estimate_head_direction(faces[0], w, h)
                    if direction in ("LEFT", "RIGHT", "DOWN"):
                        anomaly, details = f"LOOKING_{direction}", f"Head turned {direction.lower()}"

                now = time.monotonic()
                for a in list(since):          # anomaly ended -> reset
                    if a != anomaly:
                        del since[a]
                        active.discard(a)
                if anomaly:
                    since.setdefault(anomaly, now)
                    if now - since[anomaly] >= self.hold and anomaly not in active:
                        active.add(anomaly)
                        self.logger.log_event(anomaly, details)
                        self.shots.capture(frame, anomaly)

                alert = bool(active)
                self._set(camera_status="ONLINE", face_count=count, head_direction=direction,
                          system_status="ALERT: " + ", ".join(sorted(active)) if alert else "NORMAL")

                view = frame.copy()
                color = (0, 0, 255) if alert else (0, 200, 0)
                cv2.putText(view, f"Faces: {count}  Head: {direction}", (15, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                ok2, buf = cv2.imencode(".jpg", view)
                if ok2:
                    with self.lock:
                        self.jpeg = buf.tobytes()
        finally:
            cap.release()
