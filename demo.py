#!/usr/bin/env python3
"""Generate a complete IELTS Reading teaching and marking demo with one command.

No external dependencies, network access, or language-model credentials needed.
Run from any working directory: python /path/to/ielts-reading-tutor/demo.py
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL = ROOT / "skills" / "ielts-reading-tutor"
SCRIPT = SKILL / "scripts" / "ielts_tool.py"
DATASET_PATH = SKILL / "assets" / "sample-exercise.json"
RESPONSES_PATH = SKILL / "assets" / "sample-responses.json"


def load_tool():
    spec = importlib.util.spec_from_file_location("ielts_reading_tool", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load script at {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_demo(output_dir: Path) -> dict:
    tool = load_tool()
    dataset = tool.read_json(DATASET_PATH)
    errors = tool.validate(dataset)
    if errors:
        raise ValueError("Sample data validation failed:\n" + "\n".join(errors))
    responses = tool.read_json(RESPONSES_PATH)
    result = tool.grade(dataset, responses)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_files = {
        "student-worksheet.md": tool.render_student(dataset),
        "teacher-answer-key.md": tool.render_teacher(dataset),
        "student-feedback.md": tool.grade_markdown(result),
        "student-results.json": json.dumps(result, indent=2, ensure_ascii=False),
    }
    for filename, content in output_files.items():
        (output_dir / filename).write_text(content + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the IELTS Reading Tutor sample demo")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "demo-output", help="Where generated files are written")
    args = parser.parse_args()
    try:
        result = build_demo(args.output_dir)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Error: {exc}\n")
    print("IELTS Reading Tutor | Demo complete")
    print("Module: IELTS READING (not Speaking, Listening, or Writing)")
    print("Target learners: Chinese-speaking students, Band 4.5–6.0")
    print(f"Reading practice: {result['total']} questions | {result['correct']} correct | {result['accuracy_percent']}% accuracy")
    print(f"Generated: {args.output_dir.resolve()}")
    for filename in ("student-worksheet.md", "teacher-answer-key.md", "student-feedback.md", "student-results.json"):
        print(f"  - {filename}")
    print("Note: Practice accuracy is not an official IELTS band score.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
