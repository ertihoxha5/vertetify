import unittest
from unittest.mock import patch

from proof import commitment
from registry import RegistryError, envelope, verify

VECTOR = dict(
    award_date="2026-06-30",
    award_name="BSc",
    credential_id="00000000-0000-4000-8000-000000000001",
    issuer_id="demo-issuer-01",
    profile_version="vertetify-diploma-v1",
    program_name="Shkencë Kompjuterike",
    subject_display_name="Drita Demo",
)


class ProofTests(unittest.TestCase):
    def test_plan_vector(self):
        nonce = bytes(range(32))
        digest = commitment(VECTOR, nonce)
        self.assertEqual(
            digest, "1badf15b2cb1f823c806137608fac08188f03d9fc5f138b8cc1ec9c8d7e38be3"
        )
        self.assertEqual(
            digest, commitment(dict(reversed(list(VECTOR.items()))), nonce)
        )
        self.assertEqual(
            digest,
            commitment(dict(VECTOR, program_name="Shkence\u0308 Kompjuterike"), nonce),
        )
        self.assertNotEqual(digest, commitment(VECTOR, bytes(32)))
        self.assertNotEqual(digest, commitment(dict(VECTOR, award_name="MSc"), nonce))
        self.assertEqual(set(envelope(digest)), {"type", "commitment"})

    def test_sim_reference_rejected_before_io(self):
        with patch("registry.request") as transport, self.assertRaises(RegistryError):
            verify("sim-123", "0" * 64)
        transport.assert_not_called()
