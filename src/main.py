import asyncio
import csv, os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from monitor import Monitor

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = PROJECT_ROOT / "logs" / "interview_events.csv"
SCREENSHOTS_DIR = PROJECT_ROOT / "screenshots"
STATIC_DIR = Path(__file__).resolve().parent / "static"
SCREENSHOTS_DIR.mkdir(exist_ok=True)

monitor = Monitor()


@asynccontextmanager
async def lifespan(app):
    monitor.start()
    yield
    monitor.stop()


app = FastAPI(title="AI Interview Monitoring Backend", lifespan=lifespan)
app.mount("/screenshots", StaticFiles(directory=str(SCREENSHOTS_DIR)), name="screenshots")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def read_root():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/status")
def get_status():
    return monitor.get_status()


@app.get("/api/events")
def get_events():
    if not LOG_PATH.exists():
        return {"events": []}
    try:
        with open(LOG_PATH, newline="") as f:
            rows = list(csv.DictReader(f))
        return {"events": rows[-10:][::-1]}  # newest first
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/screenshots")
def get_screenshots():
    files = sorted(SCREENSHOTS_DIR.glob("*.jpg"), key=os.path.getmtime, reverse=True)
    return {"screenshots": [p.name for p in files[:8]]}


@app.get("/video_feed")
async def video_feed(request: Request):
    async def gen():
        while (
            not monitor.stop_event.is_set()
            and not await request.is_disconnected()
        ):
            j = monitor.get_jpeg()
            if j:
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + j + b"\r\n"
            await asyncio.sleep(0.05)
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace; boundary=frame")
