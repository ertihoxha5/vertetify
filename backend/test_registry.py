import hashlib
import unittest
from unittest.mock import patch

import rfc8785

import registry


class RegistryContractTests(unittest.TestCase):
    def setUp(self):
        self.ref = "urn:tar:eip155.31337:" + "1" * 40
        self.digest = "2" * 64
        payload = registry.envelope(self.digest)
        self.checksum = hashlib.sha256(rfc8785.dumps(payload)).hexdigest()
        self.tar = dict(
            id=self.ref, version=1, data=payload, checksum="0x" + self.checksum
        )

    def verify(self, latest, historical, chain):
        with (
            patch("registry.check_chain"),
            patch("registry.request", side_effect=[latest, historical]),
            patch("registry.contract_checksum", return_value=chain),
        ):
            return registry.verify(self.ref, self.digest)

    def test_three_way_match(self):
        self.assertEqual(self.verify(self.tar, self.tar, self.checksum), self.checksum)

    def test_mismatch_fails_closed(self):
        for key, value in (
            ("id", "sim-12"),
            ("version", True),
            ("version", 2),
            ("checksum", "0x00"),
            ("data", {}),
        ):
            with (
                self.subTest(key=key, value=value),
                self.assertRaises(registry.RegistryError),
            ):
                self.verify(self.tar, dict(self.tar, **{key: value}), self.checksum)
        with self.assertRaises(registry.RegistryError):
            self.verify(self.tar, self.tar, "3" * 64)

    def test_create_response_must_match_submitted_payload(self):
        with patch("registry.check_chain"), patch("registry.request", return_value=dict(self.tar, checksum="0x00")):
            with self.assertRaisesRegex(registry.RegistryError, "evidence_mismatch"):
                registry.register(self.digest)

    def test_profile_is_bound_to_new_envelope(self):
        profile = "urn:tar:eip155.31337:" + "a" * 40
        with patch("registry.verify_record", return_value=self.checksum) as read:
            registry.verify(self.ref, self.digest, profile)
        self.assertEqual(read.call_args_list[0].args, (profile, registry.PROFILE))
        self.assertEqual(read.call_args_list[1].args, (self.ref, dict(self.tar["data"], **{"@context": profile})))
        with self.assertRaisesRegex(registry.RegistryError, "evidence_mismatch"):
            self.verify(dict(self.tar, version=2), self.tar, self.checksum)

    def test_wrong_chain_before_write(self):
        with (
            patch("registry.rpc", return_value="0x1"),
            patch("registry.request") as post,
            self.assertRaises(registry.RegistryError),
        ):
            registry.register(self.digest)
        post.assert_not_called()

    def test_incomplete_rpc_evidence(self):
        with (
            patch("registry.rpc", return_value="0x"),
            self.assertRaises(registry.RegistryError),
        ):
            registry.contract_checksum("1" * 40, 1)

    def test_rest_version_one_is_contract_slot_zero(self):
        with patch(
            "registry.rpc",
            side_effect=["0x8", "0x" + format(1, "064x"), "0x" + self.checksum],
        ) as rpc:
            self.assertEqual(registry.contract_checksum("1" * 40, 1), self.checksum)
        call = rpc.call_args.args[1]
        self.assertEqual(call[0]["data"][-64:], "0" * 64)
        self.assertEqual(call[1], "0x8")
        self.assertTrue(registry.TAR.fullmatch(self.ref.replace(":1111", ":0x1111")))
