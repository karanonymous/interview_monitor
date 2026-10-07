import os
import time
from datetime import datetime
import cv2

class ScreenshotManager:
    def __init__(self, output_dir="screenshots", cooldown=5.0):
        self.output_dir = output_dir
        self.cooldown = cooldown  # Seconds between captures for the same anomaly type
        self.last_capture_times = {}
        
        # Ensure the screenshots folder exists
        os.makedirs(self.output_dir, exist_ok=True)

    def capture(self, frame, anomaly_type):
        """
        Captures and saves a frame when an anomaly occurs.
        Returns the saved filename if successful, otherwise None.
        """
        current_time = time.monotonic()
        
        # Check cooldown to prevent flooding disk storage
        last_time = self.last_capture_times.get(anomaly_type, 0)
        if current_time - last_time < self.cooldown:
            return None

        # Generate unique timestamped filename
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{anomaly_type}_{timestamp_str}.jpg"
        filepath = os.path.join(self.output_dir, filename)

        # Save frame using OpenCV
        success = cv2.imwrite(filepath, frame)
        
        if success:
            self.last_capture_times[anomaly_type] = current_time
            print(f"[SCREENSHOT SAVED] {filename}")
            return filename
        else:
            print(f"[ERROR] Failed to save screenshot: {filepath}")
            return None