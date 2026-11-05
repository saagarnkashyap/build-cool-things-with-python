"""Lifecycle for one local dashboard process, independent of the Tk interface."""

import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import urllib.request

PROJECT_DIR = Path(__file__).resolve().parent


def preferred_python(repository: Path | None = None) -> Path:
    repository = repository or PROJECT_DIR.parents[1]
    candidate = repository / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    return candidate if candidate.is_file() else Path(sys.executable)


def free_port() -> int:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        return listener.getsockname()[1]


class DashboardServer:
    """Start and stop only the child process owned by this launcher."""

    def __init__(self, python: Path | None = None):
        self.python = python or preferred_python()
        self.process = None
        self.log = None
        self.url = None

    def start(self) -> None:
        if self.process is not None and self.process.poll() is None:
            return
        self.stop()
        port = free_port()
        self.url = f"http://127.0.0.1:{port}"
        self.log = tempfile.TemporaryFile()
        try:
            self.process = subprocess.Popen(
                [str(self.python), "-m", "streamlit", "run", str(PROJECT_DIR / "app.py"),
                 "--server.address=127.0.0.1", f"--server.port={port}", "--server.headless=true",
                 "--server.fileWatcherType=none", "--browser.gatherUsageStats=false"],
                stdout=self.log, stderr=subprocess.STDOUT, cwd=PROJECT_DIR,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except OSError:
            self.log.close()
            self.log = None
            self.url = None
            raise

    def healthy(self) -> bool:
        if self.process is None or self.process.poll() is not None or self.url is None:
            return False
        try:
            with urllib.request.urlopen(self.url + "/_stcore/health", timeout=0.2) as response:
                return response.status == 200
        except OSError:
            return False

    def diagnostics(self) -> str:
        if self.log is None:
            return "No startup details available."
        self.log.seek(0)
        return self.log.read().decode("utf-8", errors="replace")[-4000:]

    def stop(self) -> None:
        if self.process is not None:
            if self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=5)
            self.process = None
        if self.log is not None:
            self.log.close()
            self.log = None
        self.url = None
