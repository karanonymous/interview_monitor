# AI Interview Monitor
```
pip install -r requirements.txt
python download_model.py     # fetches face_landmarker.task (run once)
python run.py                # open http://127.0.0.1:8000
```
Detects: no face, multiple faces, looking left/right/down (held for 2s). Events -> `logs/interview_events.csv`, screenshots -> `screenshots/`.
Tune sensitivity: `hold_seconds` in `src/monitor.py`, thresholds in `src/head_orientation.py`.
