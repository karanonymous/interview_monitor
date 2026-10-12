import threading
import sys
from pathlib import Path

import uvicorn

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from main import app, monitor


def wait_for_console_exit(server):
    while not server.should_exit:
        try:
            command = input().strip().lower()
        except EOFError:
            return

        if command in {"q", "quit", "exit"}:
            print("Stopping Interview Monitor...")
            request_stop(server)
            return

        print("Type q and press Enter to stop Interview Monitor.")


def request_stop(server):
    monitor.stop_event.set()
    server.should_exit = True


class InterviewMonitorServer(uvicorn.Server):
    def handle_exit(self, sig, frame):
        monitor.stop_event.set()
        super().handle_exit(sig, frame)


if __name__ == "__main__":
    server = InterviewMonitorServer(
        uvicorn.Config(
            app,
            host="127.0.0.1",
            port=8000,
            timeout_graceful_shutdown=3,
        )
    )
    print("Interview Monitor running. Press Ctrl+C or type q and press Enter to stop.")
    threading.Thread(target=wait_for_console_exit, args=(server,), daemon=True).start()
    server.run()
