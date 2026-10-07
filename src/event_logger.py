from pathlib import Path
from datetime import datetime
import csv

HEADER = ["timestamp", "anomaly_type", "details"]


class EventLogger:
    def __init__(self, log_file="logs/interview_events.csv"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_file.exists():
            with open(self.log_file, "w", newline="") as f:
                csv.writer(f).writerow(HEADER)

    def log_event(self, anomaly_type, details=""):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a", newline="") as f:
            csv.writer(f).writerow([ts, anomaly_type, details])
        print(f"[EVENT] {ts} - {anomaly_type}: {details}")
