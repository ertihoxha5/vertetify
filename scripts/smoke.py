"""Build an isolated Compose project and verify it via its loopback HTTP port."""
import json
import os
import subprocess
import time
import uuid
from urllib.request import urlopen
from pathlib import Path
from secrets import token_urlsafe

root = Path(__file__).resolve().parents[1]
project = "vertetify-test-" + uuid.uuid4().hex[:12]
env = dict(os.environ, POSTGRES_PASSWORD=token_urlsafe(32), WEB_PORT="0", APP_ENV="local", REGISTRY_MODE="simulator")


def compose(*args, capture=False):
    return subprocess.run(["docker", "compose", "-p", project, *args], cwd=root, env=env,
                          check=True, text=True, stdout=subprocess.PIPE if capture else None).stdout


def check(url, condition):
    with urlopen(url, timeout=5) as response:
        if not condition(response.read().decode()):
            raise RuntimeError(f"Unexpected response at {url}")


if __name__ == "__main__":
    try:
        started = time.monotonic()
        compose("up", "--build", "--wait", "--wait-timeout", "120")
        print(f"Fresh stack ready in {time.monotonic() - started:.1f}s", flush=True)
        address = compose("port", "web", "8000", capture=True).strip()
        base = "http://" + address
        check(base, lambda body: 'id="root"' in body)
        check(base + "/api/health/live", lambda body: json.loads(body)["status"] == "alive")
        check(base + "/api/health/ready", lambda body: json.loads(body)["status"] == "ready")
        check(base + "/api/workspace", lambda body: json.loads(body)["mode"] == "simulator")
        compose("exec", "-T", "web", "python", "-m", "unittest", "-v")
        compose("run", "--rm", "--no-deps", "worker", "python", "worker.py", "rehearse")
        print("Local simulator HTTP and database checks passed.")
    finally:
        compose("down", "-v", "--remove-orphans", "--rmi", "local")
