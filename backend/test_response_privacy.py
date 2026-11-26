"""HTTP privacy checks on the disposable local stack."""

import json
import os
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen


@unittest.skipUnless(
    os.getenv("VERTETIFY_ISOLATED_TEST") == "1", "requires disposable stack"
)
class ResponsePrivacyTests(unittest.TestCase):
    def test_rejected_requests_withhold_input_and_set_private_headers(self):
        origin = "http://127.0.0.1:8000"
        marker = "synthetic-validation-marker"
        cases = [
            ("public/verify", {"token": marker}, origin, 422),
            ("access/activate", {"token": marker}, origin, 422),
            (
                "session",
                {"member": "fixture-holder", "password": marker * 6},
                origin,
                422,
            ),
            ("public/verify", {"token": marker}, "", 403),
        ]
        for path, body, supplied_origin, status in cases:
            with self.subTest(path=path, status=status):
                req = Request(
                    origin + "/api/v1/" + path,
                    data=json.dumps(body).encode(),
                    headers={
                        "Origin": supplied_origin,
                        "X-Vertetify": "workspace",
                        "Content-Type": "application/json",
                    },
                )
                with self.assertRaises(HTTPError) as rejected:
                    urlopen(req, timeout=5)
                with rejected.exception as response:
                    self.assertEqual(response.code, status)
                    self.assertNotIn(marker.encode(), response.read())
                    self.assertEqual(response.headers["Cache-Control"], "no-store")
                    self.assertEqual(response.headers["Referrer-Policy"], "no-referrer")
