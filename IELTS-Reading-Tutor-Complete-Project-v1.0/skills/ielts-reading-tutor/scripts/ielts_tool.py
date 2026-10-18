#!/usr/bin/env python3
"""Deterministic IELTS reading exercise validator, renderer and grader.

Pure Python standard library; no model, network or official IELTS content.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

SUPPORTED_TYPES = {"tfng", "ynng", "multiple_choice", "matching_headings", "short_answer"}
TRUE_FALSE_NG = {"TRUE", "FALSE", "NOT GIVEN"}
YES_NO_NG = {"YES", "NO", "NOT GIVEN"}


def read_json(path: str | Path) -> dict:
    p = Path(path)
    try:
        obj = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read JSON file {p}: {exc}") from exc
    if not isinstance(obj, dict):
        raise ValueError(f"Expected a JSON object in {p}")
    return obj


def text_normalize(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value)).strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .,!?:;\"'‘’“”")


def choice_normalize(value: object, question_type: str) -> str:
    text = text_normalize(value).upper()
    if question_type in {"tfng", "ynng"}:
        aliases = {"T": "TRUE", "F": "FALSE", "NG": "NOT GIVEN", "N.G": "NOT GIVEN", "N.G.": "NOT GIVEN", "NOTGIVEN": "NOT GIVEN", "Y": "YES", "N": "NO"}
        return aliases.get(text, text)
    return text


def _assert(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate(dataset: dict) -> list[str]:
    errors: list[str] = []
    meta = dataset.get("meta")
    _assert(isinstance(meta, dict), "meta must be an object", errors)
    if isinstance(meta, dict):
        _assert(bool(meta.get("title")), "meta.title is required", errors)
        _assert(bool(meta.get("source")), "meta.source is required", errors)
    paragraphs = dataset.get("paragraphs")
    _assert(isinstance(paragraphs, list) and bool(paragraphs), "paragraphs must be a nonempty array", errors)
    pmap: dict[str, str] = {}
    if isinstance(paragraphs, list):
        for idx, item in enumerate(paragraphs, 1):
            if not isinstance(item, dict):
                errors.append(f"paragraph {idx} must be an object")
                continue
            label, passage = item.get("label"), item.get("text")
            if not isinstance(label, str) or not label.strip() or not isinstance(passage, str) or not passage.strip():
                errors.append(f"paragraph {idx} requires nonempty label and text")
                continue
            if label in pmap:
                errors.append(f"duplicate paragraph label: {label}")
            pmap[label] = passage
    headings = dataset.get("heading_bank", {})
    _assert(isinstance(headings, dict), "heading_bank must be an object", errors)
    headings = headings if isinstance(headings, dict) else {}
    questions = dataset.get("questions")
    _assert(isinstance(questions, list) and bool(questions), "questions must be a nonempty array", errors)
    if not isinstance(questions, list):
        return errors
    ids = []
    for i, item in enumerate(questions, 1):
        if not isinstance(item, dict):
            errors.append(f"question {i} must be an object")
            continue
        id_, type_, prompt, answer = item.get("id"), item.get("type"), item.get("prompt"), item.get("answer")
        prefix = f"question {id_ if id_ is not None else i}"
        if not isinstance(id_, int) or isinstance(id_, bool) or id_ < 1:
            errors.append(f"{prefix}: id must be a positive integer")
        else:
            ids.append(id_)
        if type_ not in SUPPORTED_TYPES:
            errors.append(f"{prefix}: unsupported type {type_!r}")
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append(f"{prefix}: prompt is required")
        if not isinstance(answer, str) or not answer.strip():
            errors.append(f"{prefix}: answer must be a nonempty string")
            answer = ""
        alternatives = item.get("alternatives", [])
        if not isinstance(alternatives, list) or any(not isinstance(x, str) for x in alternatives):
            errors.append(f"{prefix}: alternatives must be a list of strings")
            alternatives = []
        for field in ("explanation_zh", "skill"):
            if not isinstance(item.get(field), str) or not item.get(field, "").strip():
                errors.append(f"{prefix}: {field} is required")
        evidence = item.get("evidence")
        if not isinstance(evidence, dict):
            errors.append(f"{prefix}: evidence must be an object")
        else:
            location, quote = evidence.get("paragraph"), evidence.get("quote")
            if location not in pmap:
                errors.append(f"{prefix}: evidence paragraph does not exist: {location!r}")
            if not isinstance(quote, str) or not quote.strip():
                errors.append(f"{prefix}: evidence quote is empty")
            elif location in pmap and text_normalize(quote) not in text_normalize(pmap[location]):
                errors.append(f"{prefix}: evidence quote was not found in paragraph {location}")
        if type_ == "tfng" and choice_normalize(answer, type_) not in TRUE_FALSE_NG:
            errors.append(f"{prefix}: tfng must have TRUE, FALSE or NOT GIVEN answer")
        if type_ == "ynng" and choice_normalize(answer, type_) not in YES_NO_NG:
            errors.append(f"{prefix}: ynng must have YES, NO or NOT GIVEN answer")
        if type_ == "multiple_choice":
            options = item.get("options")
            if not isinstance(options, dict) or len(options) < 2 or any(not isinstance(k, str) or not isinstance(v, str) for k, v in options.items()):
                errors.append(f"{prefix}: multiple_choice requires an options object with >=2 entries")
            elif choice_normalize(answer, type_) not in {k.upper() for k in options}:
                errors.append(f"{prefix}: answer is not an option letter")
        if type_ == "matching_headings" and answer not in headings:
            errors.append(f"{prefix}: answer is not in heading_bank")
        if type_ == "short_answer":
            limit = item.get("word_limit")
            if not isinstance(limit, int) or isinstance(limit, bool) or limit < 1:
                errors.append(f"{prefix}: short_answer requires positive word_limit")
            else:
                for candidate in [answer, *alternatives]:
                    if len(candidate.strip().split()) > limit:
                        errors.append(f"{prefix}: answer or alternative exceeds {limit}-word limit")
    if ids != list(range(1, len(questions) + 1)):
        errors.append("question ids must be unique and sequential from 1")
    return errors


def heading_table(dataset: dict) -> str:
    return "\n".join(f"- **{label}.** {title}" for label, title in dataset.get("heading_bank", {}).items())


def render_student(dataset: dict) -> str:
    meta = dataset["meta"]
    lines = [f"# {meta['title']}", "", f"**Original practice / 原创练习** · Suggested level: {meta.get('level', 'mixed')} · Time: {meta.get('minutes', 'n/a')} minutes", "", f"*{meta['source']}*", "", "## Reading passage", ""]
    for paragraph in dataset["paragraphs"]:
        lines += [f"**{paragraph['label']}.** {paragraph['text']}", ""]
    lines += ["## Questions", "", meta.get("instructions", "Answer all questions from the passage."), ""]
    if dataset.get("heading_bank") and any(q["type"] == "matching_headings" for q in dataset["questions"]):
        lines += ["**Heading bank for matching-headings questions**", "", heading_table(dataset), ""]
    for q in dataset["questions"]:
        lines.append(f"**{q['id']}.** {q['prompt']}")
        if q["type"] == "multiple_choice":
            for letter, wording in q["options"].items():
                lines.append(f"   - {letter}. {wording}")
        lines.append("")
    lines += ["## Answer sheet", "", "| Question | Your answer |", "|:--|:--|", *[f"| {q['id']} | __________ |" for q in dataset["questions"]], ""]
    return "\n".join(lines)


def render_teacher(dataset: dict) -> str:
    lines = [render_student(dataset), "\n---", "", "# 教师版 · Answer key & evidence", "", "**注意：以上学生版可以独立复制；以下内容包含答案。**", ""]
    for q in dataset["questions"]:
        ev = q["evidence"]
        lines += [f"### Q{q['id']} — {q['answer']}", "", f"- **Evidence / 定位：** Paragraph {ev['paragraph']}: “{ev['quote']}”", f"- **解析：** {q['explanation_zh']}", f"- **考点：** `{q['skill']}`", ""]
    return "\n".join(lines)


def grade(dataset: dict, responses: dict) -> dict:
    items = []
    for q in dataset["questions"]:
        id_, qtype = q["id"], q["type"]
        value = responses.get(str(id_), responses.get(id_, ""))
        submitted = str(value).strip() if value is not None else ""
        correct_answers = [q["answer"], *q.get("alternatives", [])]
        is_correct = bool(submitted) and any(choice_normalize(submitted, qtype) == choice_normalize(expected, qtype) for expected in correct_answers)
        items.append({"id":id_, "type":qtype, "given":submitted, "expected":q["answer"], "correct":is_correct, "attempted":bool(submitted), "evidence":q["evidence"], "explanation_zh":q["explanation_zh"], "skill":q["skill"]})
    total = len(items)
    attempted = sum(x["attempted"] for x in items)
    correct = sum(x["correct"] for x in items)
    by_type = {kind:{"correct":sum(x["correct"] for x in sub), "total":len(sub)} for kind in dict.fromkeys(x["type"] for x in items) if (sub := [x for x in items if x["type"] == kind])}
    error_focus = [name for name, count in Counter(x["skill"] for x in items if x["attempted"] and not x["correct"]).most_common(3)]
    return {"total":total,"attempted":attempted,"correct":correct,"accuracy_percent":round(100*correct/total,1) if total else 0,"by_type":by_type,"error_focus":error_focus,"items":items}


def grade_markdown(result: dict) -> str:
    lines = ["# 雅思阅读练习反馈 / Practice feedback", "", f"**正确：{result['correct']}/{result['total']}** · 已作答：{result['attempted']}/{result['total']} · **练习准确率：{result['accuracy_percent']}%**", "", "> 本练习为原创教学材料；准确率不等于官方 IELTS Band Score。", "", "## 逐题反馈", ""]
    for item in result["items"]:
        status = "✓" if item["correct"] else ("未作答" if not item["attempted"] else "✗")
        given = item["given"] or "（空白）"
        ev = item["evidence"]
        lines += [f"**Q{item['id']} {status}** · Your answer: `{given}` · Key: **{item['expected']}**", "", f"- **定位：** Paragraph {ev['paragraph']}: “{ev['quote']}”", f"- **解析：** {item['explanation_zh']}", ""]
    lines += ["## 分题型表现", "", "| Type | Correct | Total |", "|:--|--:|--:|"]
    lines += [f"| {kind} | {counts['correct']} | {counts['total']} |" for kind,counts in result["by_type"].items()]
    lines += ["", "**建议优先练习：** " + ("、".join(result["error_focus"]) if result["error_focus"] else "维持原文定位与逐题核对。"), "", "*短答案采用标准化后精确匹配；请人工核对合理的未列入同义答案。*", ""]
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Original IELTS-style Reading practice CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "render", "grade"):
        cmd = subparsers.add_parser(name)
        cmd.add_argument("--dataset", required=True, help="Exercise JSON")
        if name == "render":
            cmd.add_argument("--mode", choices=("student", "teacher"), default="student")
            cmd.add_argument("--output", help="Markdown output file (defaults to stdout)")
        if name == "grade":
            cmd.add_argument("--answers", required=True, help="JSON object mapping question numbers to student answers")
            cmd.add_argument("--format", choices=("markdown", "json"), default="markdown")
            cmd.add_argument("--output", help="Feedback file (defaults to stdout)")
    args = parser.parse_args(argv)
    try:
        dataset = read_json(args.dataset)
        errors = validate(dataset)
        if errors:
            print("Validation failed:\n" + "\n".join(f"- {e}" for e in errors), file=sys.stderr)
            return 2
        if args.command == "validate":
            print(f"OK: {len(dataset['paragraphs'])} paragraphs, {len(dataset['questions'])} questions; evidence quotes found.")
            print("Note: logical entailment and alternative-answer acceptability still need human review.")
            return 0
        if args.command == "render":
            output = render_student(dataset) if args.mode == "student" else render_teacher(dataset)
        else:
            responses = read_json(args.answers)
            result = grade(dataset, responses)
            output = json.dumps(result,ensure_ascii=False,indent=2) if args.format == "json" else grade_markdown(result)
        if args.output:
            destination = Path(args.output)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(output + "\n", encoding="utf-8")
            print(f"Wrote {destination}")
        else:
            print(output)
        return 0
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
