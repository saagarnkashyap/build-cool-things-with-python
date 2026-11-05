import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.error import URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from launcher import DashboardServer, preferred_python


class LauncherTests(unittest.TestCase):
    def test_prefers_local_environment_and_falls_back(self):
        with tempfile.TemporaryDirectory() as folder:
            repository = Path(folder)
            self.assertEqual(preferred_python(repository), Path(sys.executable))
            candidate = repository / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            candidate.parent.mkdir(parents=True)
            candidate.touch()
            self.assertEqual(preferred_python(repository), candidate)

    def test_start_is_local_and_stop_owns_only_its_child(self):
        process = Mock()
        process.poll.return_value = None
        server = DashboardServer(Path(sys.executable))
        with patch("launcher.free_port", return_value=12345), patch("launcher.subprocess.Popen", return_value=process) as spawn:
            server.start()
            server.start()
            spawn.assert_called_once()
            arguments = spawn.call_args.args[0]
            self.assertIn("--server.address=127.0.0.1", arguments)
            self.assertIn("--server.headless=true", arguments)
            self.assertEqual(server.url, "http://127.0.0.1:12345")
            log = server.log
            server.stop()
            process.terminate.assert_called_once()
            process.wait.assert_called_once()
            self.assertTrue(log.closed)
            self.assertIsNone(server.process)
            self.assertIsNone(server.url)

    def test_failed_spawn_cleans_up(self):
        server = DashboardServer(Path(sys.executable))
        with patch("launcher.free_port", return_value=12345), patch("launcher.subprocess.Popen", side_effect=OSError("missing Python")):
            with self.assertRaises(OSError):
                server.start()
        self.assertIsNone(server.log)
        self.assertIsNone(server.url)

    def test_health_check_handles_startup_and_connection_failure(self):
        server = DashboardServer(Path(sys.executable))
        self.assertFalse(server.healthy())
        server.process = Mock()
        server.process.poll.return_value = None
        server.url = "http://127.0.0.1:12345"
        with patch("launcher.urllib.request.urlopen") as request:
            request.return_value.__enter__.return_value.status = 200
            self.assertTrue(server.healthy())
        with patch("launcher.urllib.request.urlopen", side_effect=URLError("not ready")):
            self.assertFalse(server.healthy())
