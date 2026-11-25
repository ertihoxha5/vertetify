"""Temporary verifier-only HTTP bridge for one phone on a trusted private LAN."""

import argparse
import ipaddress
import json
import re
import time
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def lan_address(value):
    addr = ipaddress.IPv4Address(value)
    if not any(addr in block for block in LAN_BLOCKS):
        raise argparse.ArgumentTypeError("Choose an RFC 1918 Wi-Fi address.")
    return str(addr)


LAN_BLOCKS = tuple(
    map(ipaddress.ip_network, ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"))
)
UPSTREAM = "127.0.0.1:8184"


class PhoneServer(ThreadingHTTPServer):
    def verify_request(self, request, client_address):
        return client_address[0] in (self.phone, self.server_address[0])


class Verifier(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def forward(self, path, body=None):
        if self.headers.get("Host") != self.server.origin.removeprefix("http://"):
            self.send_error(400)
            return
        conn = HTTPConnection(UPSTREAM, timeout=30)
        try:
            headers = (
                {
                    "Content-Type": "application/json",
                    "Origin": "http://" + UPSTREAM,
                    "X-Vertetify": "workspace",
                }
                if body is not None
                else {}
            )
            conn.request(self.command, path, body=body, headers=headers)
            response = conn.getresponse()
            data = response.read()
            if path == "/api/workspace" and response.status == 200:
                data = json.dumps({"mode": json.loads(data)["mode"]}).encode()
            self.send_response(response.status)
            self.send_header(
                "Content-Type",
                response.getheader("Content-Type", "application/octet-stream"),
            )
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except (OSError, ValueError):
            self.send_error(502)
        finally:
            conn.close()

    def do_GET(self):
        if self.path in (
            "/",
            "/verify",
            "/?how",
            "/api/workspace",
            "/vertetify-logo.png",
        ) or re.fullmatch(r"/assets/[\w.-]+\.(?:js|css)", self.path):
            self.forward(self.path)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/api/v1/public/verify":
            self.send_error(404)
            return
        if (
            self.headers.get("Origin") != self.server.origin
            or self.headers.get("X-Vertetify") != "workspace"
        ):
            self.send_error(403)
            return
        size = self.headers.get("Content-Length", "")
        if not re.fullmatch(r"[0-9]{1,3}", size) or not 0 < int(size) <= 128:
            self.send_error(400)
            return
        self.forward(self.path, self.rfile.read(int(size)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bind", required=True, type=lan_address)
    parser.add_argument("--phone", required=True, type=lan_address)
    args = parser.parse_args()
    with PhoneServer((args.bind, 18184), Verifier) as server:
        server.phone = args.phone
        server.origin = f"http://{args.bind}:18184"
        server.timeout = 1
        print(
            f"Open {server.origin}/verify in Safari. Bridge closes in 20 minutes.",
            flush=True,
        )
        deadline = time.monotonic() + 1200
        while time.monotonic() < deadline:
            server.handle_request()


if __name__ == "__main__":
    main()
