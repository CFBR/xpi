# test_registry_race.py — concurrent status and frame reads see a full registry.

import concurrent.futures
import json
import os
import tempfile
import threading
import unittest
import urllib.request

import server


class RegistryRaceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = self.tmp.name
        self.scripts = os.path.join(root, "scripts")
        os.makedirs(self.scripts)
        for name in ("one.py", "two.py"):
            with open(os.path.join(self.scripts, name), "w") as fh:
                fh.write("import time\n")
        self.old = {
            "SCRIPTS_DIR": server.SCRIPTS_DIR,
            "SCAN_DIRS": server.SCAN_DIRS,
            "STATE_FILE": server.STATE_FILE,
            "CONFIG_FILE": server.CONFIG_FILE,
            "FRAME_FILE": server.FRAME_FILE,
            "SCRIPT_REGISTRY": server.SCRIPT_REGISTRY,
            "BOARD_TAGS": server.BOARD_TAGS,
            "log": server.Handler.log_message,
        }
        server.SCRIPTS_DIR = self.scripts
        server.SCAN_DIRS = [self.scripts]
        server.STATE_FILE = os.path.join(root, "state.json")
        server.CONFIG_FILE = os.path.join(root, "config.json")
        server.FRAME_FILE = os.path.join(root, "frame.json")
        server.SCRIPT_REGISTRY = {}
        server.BOARD_TAGS = {}
        server._registry_last = 0.0
        server.refresh_registry(force=True)
        server.Handler.log_message = lambda *args, **kwargs: None
        self.httpd = server.Server(("127.0.0.1", 0), server.Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever,
                                       daemon=True)
        self.thread.start()
        self.base = "http://127.0.0.1:%d" % self.httpd.server_address[1]

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=2)
        for key, value in self.old.items():
            if key == "log":
                server.Handler.log_message = value
            else:
                setattr(server, key, value)
        self.tmp.cleanup()

    def get(self, path):
        with urllib.request.urlopen(self.base + path, timeout=5) as response:
            return json.load(response)

    def test_status_never_sees_an_empty_registry(self):
        failures = []

        def worker(_):
            for _ in range(20):
                status = self.get("/?action=status")
                if not status.get("scripts") or not status.get("boards"):
                    failures.append(status)
                if len(status.get("scripts") or []) != 2:
                    failures.append(status)
                self.get("/action=frame")

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(worker, range(8)))
        self.assertEqual([], failures)


if __name__ == "__main__":
    unittest.main()
