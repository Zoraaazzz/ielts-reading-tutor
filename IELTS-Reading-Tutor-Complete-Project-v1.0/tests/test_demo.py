"""Smoke and end-to-end tests for the interview demo entry point."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DemoTests(unittest.TestCase):
    def test_one_command_generates_all_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            process = subprocess.run(
                [sys.executable, str(ROOT / "demo.py"), "--output-dir", tmpdir],
                capture_output=True, text=True, check=True, cwd=tmpdir
            )
            self.assertIn("Demo complete", process.stdout)
            self.assertIn("IELTS READING", process.stdout)
            output = Path(tmpdir)
            for name in ("student-worksheet.md", "teacher-answer-key.md", "student-feedback.md", "student-results.json"):
                self.assertTrue((output / name).is_file(), name)
                self.assertGreater((output / name).stat().st_size, 0)
            student = (output / "student-worksheet.md").read_text(encoding="utf-8")
            teacher = (output / "teacher-answer-key.md").read_text(encoding="utf-8")
            feedback = (output / "student-feedback.md").read_text(encoding="utf-8")
            results = json.loads((output / "student-results.json").read_text(encoding="utf-8"))
            self.assertNotIn("教师版", student)
            self.assertIn("教师版", teacher)
            self.assertIn("76.9%", feedback)
            self.assertEqual((results["correct"], results["total"]), (10, 13))
            self.assertIn("A. Sewing machines", student)
            self.assertIn("B. Portable projectors", student)

    def test_json_cli_result_matches_demo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = ROOT / "skills" / "ielts-reading-tutor" / "scripts" / "ielts_tool.py"
            data = ROOT / "skills" / "ielts-reading-tutor" / "assets" / "sample-exercise.json"
            answers = ROOT / "skills" / "ielts-reading-tutor" / "assets" / "sample-responses.json"
            completed = subprocess.run(
                [sys.executable, str(tool), "grade", "--dataset", str(data), "--answers", str(answers), "--format", "json"],
                capture_output=True, text=True, check=True, cwd=tmpdir
            )
            self.assertEqual(json.loads(completed.stdout)["correct"], 10)


if __name__ == "__main__":
    unittest.main()
