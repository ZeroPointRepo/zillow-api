"""Runs the Python verifier published in endpoints/webhooks.md.

No network, standard library only:
    python3 -m unittest discover -s tests
"""

import hashlib
import hmac
import json
import pathlib
import re
import time
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
SECRET = "whsec_test_only"
TIMESTAMP = 1795340000
WINDOW = 300

# Known answer produced by the API's signer for SECRET at TIMESTAMP.
SIGNER_BODY = b'{"event":"job.succeeded"}'
SIGNER_HEADER = (
    "t=1795340000,"
    "v1=b866342de8802a578bfd323e3d66a6c82ea087272a7c343ff1909909791c5036"
)


def load_documented_verifier():
    doc = (ROOT / "endpoints" / "webhooks.md").read_text(encoding="utf-8")
    blocks = [b for b in re.findall(r"```python\n(.*?)```", doc, re.S) if "def verify(" in b]
    if len(blocks) != 1:
        raise AssertionError("expected exactly one documented verify() in endpoints/webhooks.md")
    namespace = {}
    exec(blocks[0], namespace)
    return namespace["verify"]


def delivery_body(name="job.succeeded"):
    payload = {
        "event": name,
        "delivered_at": "2026-11-22T08:00:00.000Z",
        "data": {
            "job": {
                "id": "00000000-0000-4000-8000-000000000001",
                "type": "batch",
                "status": "succeeded",
                "result_count": 2,
                "created_at": "2026-11-22T07:55:00Z",
                "started_at": "2026-11-22T07:55:01Z",
                "completed_at": "2026-11-22T07:59:59Z",
            }
        },
    }
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def signature_header(body, secret=SECRET, ts=TIMESTAMP):
    """Same format as the API: t=<unix>,v1=<hex HMAC-SHA256 of '<t>.<body>'>."""
    signed = str(ts).encode() + b"." + body
    digest = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return f"t={ts},v1={digest}"


class TestDocumentedVerifier(unittest.TestCase):
    def setUp(self):
        self.verify = load_documented_verifier()
        self.body = delivery_body()
        self.header = signature_header(self.body)
        self.digest = self.header.split("v1=")[1]
        clock = patch("time.time", return_value=TIMESTAMP)
        self.clock = clock.start()
        self.addCleanup(clock.stop)

    def assert_rejected(self, *headers):
        for header in headers:
            with self.subTest(header=ascii(header)):
                self.assertIs(self.verify(self.body, header, SECRET), False)

    def test_accepts_genuine_delivery(self):
        self.assertTrue(self.verify(self.body, self.header, SECRET))

    def test_accepts_non_ascii_body(self):
        body = delivery_body("café ✓")
        self.assertTrue(self.verify(body, signature_header(body), SECRET))

    def test_rejects_tampered_body(self):
        tampered = self.body.replace(b'"result_count":2', b'"result_count":3')
        self.assertNotEqual(tampered, self.body)
        self.assertFalse(self.verify(tampered, self.header, SECRET))

    def test_rejects_reformatted_body(self):
        reformatted = json.dumps(json.loads(self.body), indent=2).encode()
        self.assertFalse(self.verify(reformatted, self.header, SECRET))

    def test_rejects_tampered_timestamp(self):
        header = self.header.replace(f"t={TIMESTAMP}", f"t={TIMESTAMP + 1}")
        self.assertNotEqual(header, self.header)
        self.assertFalse(self.verify(self.body, header, SECRET))

    def test_rejects_wrong_secret(self):
        self.assertFalse(self.verify(self.body, self.header, "whsec_other"))

    def test_rejects_signature_over_body_alone(self):
        digest = hmac.new(SECRET.encode(), self.body, hashlib.sha256).hexdigest()
        self.assertFalse(self.verify(self.body, f"t={TIMESTAMP},v1={digest}", SECRET))

    def test_accepts_known_answer_from_api_signer(self):
        self.assertTrue(self.verify(SIGNER_BODY, SIGNER_HEADER, SECRET))

    def test_accepts_fresh_delivery_on_the_real_clock(self):
        now = time.time_ns() // 1_000_000_000
        self.clock.side_effect = lambda: time.time_ns() / 1_000_000_000
        self.assertTrue(self.verify(self.body, signature_header(self.body, ts=now), SECRET))

    def test_rejects_empty_header(self):
        self.assert_rejected("", " ")

    def test_rejects_missing_header(self):
        self.assert_rejected(None)

    def test_rejects_malformed_header(self):
        t, v1 = f"t={TIMESTAMP}", f"v1={self.digest}"
        self.assert_rejected(
            "garbage",
            self.digest,  # signature without t= and v1=
            t,
            v1,
            f"{t},",
            f"t=,{v1}",
            f"t=abc,{v1}",
            f"t=-{TIMESTAMP},{v1}",
            f"t={TIMESTAMP}.0,{v1}",
            f"t={'9' * 5000},{v1}",
            f"{t},v1=",
            f"{t},v1={self.digest[:-1]}",
            f"{t},v1={self.digest}0",
            f"{t},v1={'z' * 64}",
            f"{t},v1={self.digest.upper()}",
            f"{v1},{t}",
            f"{t},{t},{v1}",
            f"{self.header},x=1",
            f"{self.header}\n",
            f" {self.header}",
            self.header.encode(),  # bytes instead of str
        )

    def test_rejects_non_ascii_header(self):
        fullwidth = "".join(chr(0xFF10 + int(d)) for d in str(TIMESTAMP))
        self.assert_rejected(
            "\u00e9",
            f"t={TIMESTAMP},v1=\u00e9{self.digest[1:]}",
            f"t={fullwidth},v1={self.digest}",
            f"{self.header}\udcff",
        )

    def test_accepts_both_edges_of_the_window(self):
        for offset in (-WINDOW, 0, WINDOW):
            with self.subTest(offset=offset):
                self.clock.return_value = TIMESTAMP + offset
                self.assertTrue(self.verify(self.body, self.header, SECRET))

    def test_rejects_timestamp_older_than_window(self):
        for age in (WINDOW + 0.001, WINDOW + 1, 86400):
            with self.subTest(age=age):
                self.clock.return_value = TIMESTAMP + age
                self.assertIs(self.verify(self.body, self.header, SECRET), False)

    def test_rejects_timestamp_further_ahead_than_window(self):
        for lead in (WINDOW + 0.001, WINDOW + 1, 86400):
            with self.subTest(lead=lead):
                self.clock.return_value = TIMESTAMP - lead
                self.assertIs(self.verify(self.body, self.header, SECRET), False)


if __name__ == "__main__":
    unittest.main()
