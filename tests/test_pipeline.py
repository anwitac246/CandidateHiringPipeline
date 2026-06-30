from __future__ import annotations

import unittest
from pathlib import Path
import sys

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.normalizer import normalize_phone, normalize_date, normalize_skill
from src.projector import project
from src.schema import CandidateRecord


class TestSanitizationAndNormalization(unittest.TestCase):
    def test_phone_normalization(self) -> None:
        self.assertEqual(normalize_phone("+1-415-555-0101"), "+14155550101")
        self.assertEqual(normalize_phone("+91-98765-10007"), "+919876510007")
        self.assertEqual(normalize_phone("098765 10011"), "+919876510011")
        self.assertEqual(normalize_phone(""), None)
        self.assertEqual(normalize_phone("   "), None)

    def test_date_normalization(self) -> None:
        self.assertEqual(normalize_date("2026-05-01"), "2026-05")
        self.assertEqual(normalize_date("Jan 2023"), "2023-01")
        self.assertEqual(normalize_date("June 2021"), "2021-06")
        self.assertEqual(normalize_date("03/2022"), "2022-03")
        self.assertEqual(normalize_date("2020"), "2020-01")
        self.assertEqual(normalize_date(None), None)

    def test_skill_canonicalization(self) -> None:
        self.assertEqual(normalize_skill("ReactJS"), "react")
        self.assertEqual(normalize_skill("react.js"), "react")
        self.assertEqual(normalize_skill("Node.js"), "node")
        self.assertEqual(normalize_skill("testing library"), "testing-library")
        self.assertEqual(normalize_skill("python"), "python")


class TestProjector(unittest.TestCase):
    def setUp(self) -> None:
        self.record = CandidateRecord(
            candidate_id="C99",
            full_name="Test Candidate",
            emails=["test@example.com", "alt@example.com"],
            phones=["+14155550100"],
            skills=[
                {"name": "react", "confidence": 1.0, "sources": ["ats_json"]}
            ]
        )

    def test_basic_projection(self) -> None:
        config = {
            "fields": [
                {"path": "candidate_id", "type": "string", "required": True},
                {"path": "full_name", "type": "string"}
            ]
        }
        res = project(self.record, config)
        self.assertEqual(res["candidate_id"], "C99")
        self.assertEqual(res["full_name"], "Test Candidate")
        self.assertNotIn("emails", res)

    def test_path_resolution(self) -> None:
        config = {
            "fields": [
                {"path": "primary_email", "from": "emails[0]", "type": "string"},
                {"path": "all_skills", "from": "skills[].name", "type": "string[]"}
            ]
        }
        res = project(self.record, config)
        self.assertEqual(res["primary_email"], "test@example.com")
        self.assertEqual(res["all_skills"], ["react"])

    def test_missing_policy_omit(self) -> None:
        config = {
            "fields": [
                {"path": "non_existent", "type": "string"}
            ],
            "on_missing": "omit"
        }
        res = project(self.record, config)
        self.assertNotIn("non_existent", res)

    def test_missing_policy_error(self) -> None:
        config = {
            "fields": [
                {"path": "non_existent", "type": "string", "required": True}
            ],
            "on_missing": "error"
        }
        with self.assertRaises(ValueError):
            project(self.record, config)


if __name__ == "__main__":
    unittest.main()
