# server.py — xpi display control webserver + script supervisor.
# Python 3 stdlib only. Serves a LAN control page and a JSON API that
# switches/restarts display scripts and patches state.json for live updates.

import argparse
import collections
import datetime
import http.server
import json
import os
import signal
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(ROOT, "state.json")
CONFIG_FILE = os.path.join(ROOT, "config.json")
INDEX_FILE = os.path.join(ROOT, "index.html")
SCRIPTS_DIR = os.path.join(ROOT, "scripts")
SCAN_DIRS = [
    SCRIPTS_DIR,
    os.path.join(ROOT, "repos/microdot-phat/examples"),
    os.path.join(ROOT, "repos/unicorn-hat/examples"),
    os.path.join(ROOT, "repos/unicorn-hat/examples/hat"),
    os.path.join(ROOT, "repos/unicorn-hat/examples/phat"),
]
REPO_LIBPATHS = [
    os.path.join(ROOT, "repos/microdot-phat/library"),
    os.path.join(ROOT, "repos/unicorn-hat/library/UnicornHat"),
]

_state_lock = threading.Lock()


# ---------------------------------------------------------------- state ---

def _read_state():
    try:
        with open(STATE_FILE) as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _write_state(data):
    tmp = tempfile.NamedTemporaryFile(
        "w", dir=ROOT, prefix=".state-", suffix=".json", delete=False)
    with tmp:
        json.dump(data, tmp)
    os.replace(tmp.name, STATE_FILE)


def bump_state(patch):
    with _state_lock:
        data = _read_state()
        data.update(patch)
        data["revision"] = data.get("revision", 0) + 1
        _write_state(data)
        return data["revision"]


# --------------------------------------------------------------- config ---

def read_config():
    try:
        with open(CONFIG_FILE) as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def write_config(data):
    with _state_lock:
        tmp = tempfile.NamedTemporaryFile(
            "w", dir=ROOT, prefix=".config-", suffix=".json", delete=False)
        with tmp:
            json.dump(data, tmp)
        os.replace(tmp.name, CONFIG_FILE)


# --------------------------------------------------------------- script ---

def scan_scripts():
    """Registry keyed by filename stem; first scan-dir occurrence wins."""
    registry = {}
    for directory in SCAN_DIRS:
        if not os.path.isdir(directory):
            continue
        for name in sorted(os.listdir(directory)):
            if not name.endswith(".py") or name.startswith("_"):
                continue
            stem = name[:-3]
            if stem in registry:
                print("server: duplicate stem %r, keeping %s"
                      % (stem, registry[stem]))
                continue
            registry[stem] = os.path.join(directory, name)
    return registry


SCRIPT_REGISTRY = {}
_child = None
_child_args = []
_child_started = None
_log_lock = threading.Lock()
_log_chunks = collections.deque(maxlen=512)
_sup_lock = threading.RLock()  # serializes start/stop (reentrant: start calls stop)


def child_env():
    env = os.environ.copy()
    inherited = env.get("PYTHONPATH", "")
    extra = [SCRIPTS_DIR] + [p for p in REPO_LIBPATHS if os.path.isdir(p)]
    joined = ":".join(extra)
    env["PYTHONPATH"] = inherited + ":" + joined if inherited else joined
    return env


def _pump(stdout):
    try:
        while True:
            data = os.read(stdout.fileno(), 1024)
            if not data:
                break
            with _log_lock:
                for i in range(0, len(data), 128):
                    _log_chunks.append(data[i:i + 128])
    except OSError:
        pass


def start_child(stem, args=()):
    global _child, _child_args, _child_started
    path = SCRIPT_REGISTRY[stem]
    with _sup_lock:
        stop_child()
        with _log_lock:
            _log_chunks.clear()
        _child = subprocess.Popen(
            [sys.executable, "-u", path, *args],
            cwd=os.path.dirname(path), env=child_env(),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        _child_args = list(args)
        _child_started = time.time()
    threading.Thread(target=_pump, args=(_child.stdout,), daemon=True).start()
    print("server: started %s (pid %d)" % (stem, _child.pid))


def stop_child():
    """SIGINT -> 2 s -> SIGTERM -> 2 s -> SIGKILL."""
    global _child, _child_args, _child_started
    if _child is None:
        return
    with _sup_lock:
        child = _child
        _child = None
        _child_args = []
        _child_started = None
        for sig_int in (signal.SIGINT, signal.SIGTERM, signal.SIGKILL):
            if child.poll() is not None:
                break
            child.send_signal(sig_int)
            deadline = time.time() + 2
            while time.time() < deadline and child.poll() is None:
                time.sleep(0.05)
        child.wait()
        with _log_lock:
            _log_chunks.append(b"[%d stopped]\n" % child.pid)
        print("server: stopped pid %d" % child.pid)


def running_child():
    if _child is not None and _child.poll() is not None:
        return None          # died on its own; not "running"
    return _child


def log_text(tail=1200):
    with _log_lock:
        return b"".join(_log_chunks).decode("utf-8", "replace")[-tail:]


def clear_board():
    with _sup_lock:
        stop_child()
        result = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS_DIR, "clear.py")],
            cwd=SCRIPTS_DIR, env=child_env(), timeout=5,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    with _log_lock:
        _log_chunks.clear()
        for i in range(0, len(result.stdout), 128):
            _log_chunks.append(result.stdout[i:i + 128])
    return result.returncode


def status():
    child = running_child()
    started = None
    if _child_started is not None:
        started = datetime.datetime.fromtimestamp(
            _child_started, datetime.timezone.utc).isoformat()
    return {
        "running": current_stem(child),
        "pid": child.pid if child else None,
        "started": started,
        "boot": read_config().get("boot"),
        "scripts": sorted(SCRIPT_REGISTRY),
        "revision": _read_state().get("revision"),
        "log": log_text(),
    }


def current_stem(child):
    if child is None:
        return None
    # the child argv is [python, -u, script_path, ...] — match any element
    try:
        for arg in child.args[1:]:
            for stem, spath in SCRIPT_REGISTRY.items():
                if os.path.abspath(spath) == os.path.abspath(arg):
                    return stem
        return os.path.basename(child.args[-1])
    except Exception:
        return None


# ----------------------------------------------------------------- http ---

class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        print("server: %s" % (fmt % args))

    # GET and POST share the same pipeline; POST body is parsed as QS.
    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def _drain_body(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length:
            try:
                self.rfile.read(length)
            except OSError:
                pass

    def do_HEAD(self):
        self._drain_body()
        head = b""
        self.respond(200, head, "text/html")

    # ------------------------------------------------------------------ #
    def handle_request(self):
        parse = urllib.parse.urlsplit(self.path)
        path = parse.path
        try:
            params = self.parse_query(parse)
            action = (params.pop("action", [None])[0] or "").strip()
            SCRIPT_REGISTRY.clear()
            SCRIPT_REGISTRY.update(scan_scripts())
            if not action:
                if path in ("/", "/index.html"):
                    self.serve_index()
                else:
                    self.respond(404, {"error": "no action"})
                return
            self._drain_body()
            if action == "update":
                self.act_update(params)
            elif action == "switch":
                self.act_switch(params)
            elif action == "stop":
                self.act_stop()
            elif action == "clear":
                self.act_clear()
            elif action == "boot":
                self.act_boot(params)
            elif action in ("status", "scripts"):
                self.respond(200, status(), "json")
            else:
                self.respond(404, {"error": "unknown action", "action": action})
        except (BrokenPipeError, ConnectionResetError):
            self.close_connection = True
            raise
        except Exception as exc:      # keep server alive on handler bugs
            self.respond(500, {"error": "%s: %s"
                               % (type(exc).__name__, exc)})

    @staticmethod
    def parse_query(parse):
        qs = parse.query
        if not qs:
            tail = parse.path.lstrip("/")
            if tail.startswith("action="):
                qs = tail          # tolerate /action=update&script=... (no ?)
        return urllib.parse.parse_qs(qs)

    def act_update(self, params):
        script = params.pop("script", [None])[0]
        args = params.pop("arg", [])
        if script and script not in SCRIPT_REGISTRY:
            self.respond(404, {"error": "unknown script", "script": script})
            return
        patch = {k: values[0] for k, values in params.items()}
        revision = bump_state(patch)
        if script:
            start_child(script, args=args)
        self.respond(200, {"ok": True, "revision": revision})

    def act_switch(self, params):
        script = params.pop("script", [None])[0]
        args = params.pop("arg", [])
        if not script:
            self.respond(400, {"error": "script required"})
            return
        if script not in SCRIPT_REGISTRY:
            self.respond(404, {"error": "unknown script", "script": script})
            return
        start_child(script, args=args)
        self.respond(200, {"ok": True, "running": script})

    def act_stop(self):
        stop_child()
        self.respond(200, {"ok": True, "running": None})

    def act_clear(self):
        clear_board()
        self.respond(200, {"ok": True, "running": None})

    def act_boot(self, params):
        script = params.pop("script", [None])[0]
        if script in (None, "") or script == "none":
            write_config({"boot": None})
            return self.respond(200, {"ok": True, "boot": None})
        if script not in SCRIPT_REGISTRY:
            return self.respond(404, {"error": "unknown script",
                                      "script": script})
        write_config({"boot": script})
        self.respond(200, {"ok": True, "boot": script})

    def serve_index(self):
        try:
            with open(INDEX_FILE, "rb") as fh:
                body = fh.read()
        except OSError:
            return self.respond(404, {"error": "index.html missing"})
        self.respond(200, body, "text/html")

    # --------------------------------------------------------------- out --
    def respond(self, code, payload, kind="json"):
        ctype = {"json": "application/json", "html": "text/html"}.get(
            kind)
        if ctype is None:
            ctype = kind if kind in ("text/html", "text/plain") \
                else "application/json"
        if kind == "json":
            body = json.dumps(payload).encode()
        else:
            body = payload.encode() if isinstance(payload, str) else payload
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)


class Server(http.server.ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    global SCRIPT_REGISTRY
    parser = argparse.ArgumentParser(
        description="xpi display control webserver (stdlib only)")
    parser.add_argument("--port", type=int, default=80)
    parser.add_argument("--bind", default="0.0.0.0")
    args = parser.parse_args()

    SCRIPT_REGISTRY.update(scan_scripts())
    boot = read_config().get("boot")
    if boot:
        if boot in SCRIPT_REGISTRY:
            start_child(boot)
        else:
            print("server: boot script %r not found; starting without"
                  % boot)

    def shutdown(signum, frame):
        print("server: signal %s; stopping" % signum)
        stop_child()
        raise SystemExit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    httpd = Server((args.bind, args.port), Handler)
    print("server: listening on %s:%d" % (args.bind, args.port))
    try:
        httpd.serve_forever()
    except SystemExit:
        httpd.server_close()
        print("server: bye")


if __name__ == "__main__":
    main()
