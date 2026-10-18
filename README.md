# IELTS Reading Tutor | 雅思阅读专项 AI 教学 Skill

**IELTS Reading only · 阅读专项 · 中文辅助教学 · 核心目标水平 Band 4.5–6.0**

An **Agent Skill for IELTS Reading (Academic & General Training)** that helps Chinese-speaking learners understand passages, practise common reading question types, and review answers with passage-based evidence. It also helps tutors prepare separate student worksheets, answer keys, short lesson plans, and mistake-focused feedback.

> **Scope:** Reading comprehension and reading question-solving. This project does **not** teach or assess IELTS Speaking, Listening, or Writing. Band 4.5–6.0 is the default teaching level; a compatible AI agent can adjust explanations to other levels when asked. It does not predict official IELTS scores.
>
> **Unofficial, original teaching demo.** Not affiliated with IELTS, Cambridge, IDP, or the British Council. The sample passage and exercises were written for this project; they are not official IELTS exam questions.

## Features & Workflows

| Mode | User provides | Output |
| --- | --- | --- |
| **Reading tutor / 阅读精讲** | A passage, question, or unfamiliar sentence | Chinese explanation, English terminology, text location, paraphrase, and reasoning |
| **Guided practice / 题型训练** | A reading passage or requested skill focus | Original reading questions, with answers withheld in student mode |
| **Answer review / 答案解析** | Questions plus student answers | Answer-by-answer evidence, error explanations, and priorities for practice |
| **Teacher preparation / 备课** | Reading material and target level | Student worksheet, separate teacher key, and timed mini-lesson plan |
| **Python demo / 可运行演示** | Bundled sample exercise and responses | Markdown worksheets, a grading report, and JSON results |

**Key IELTS Reading topics:** TRUE / FALSE / NOT GIVEN, YES / NO / NOT GIVEN, matching headings, matching details/features, multiple choice, short answers and completion questions. The bundled dataset demonstrates **TFNG, multiple choice, matching headings, matching information, matching features, completion and short answers**. The validator and keyed grader additionally support **Y/N/NG** with a valid dataset. Other diagram/flow-chart reasoning can be taught by the Agent Skill but is not automatically graded by the current CLI.

### How the two parts work

- **Agent Skill (`SKILL.md`)**: instructions for a compatible AI agent to explain passages, teach question-solving strategies, create original exercises, and diagnose errors from provided materials.
- **Python command-line tools**: deterministic local programs that validate structured question datasets, render Markdown handouts and mark keyed student responses. They use **Python standard library only**, make **no API calls**, and do not generate passages by themselves.

There is **no separate website, mobile app, or voice interface** in this version. The immediate outputs are text/Markdown and JSON files.

## One-command Demo

**Requirements:** Python 3.10+; no package installation or API key needed. Open a terminal in the repository root:

```bash
python demo.py
```

This creates a `demo-output/` folder containing:

```text
demo-output/
├── student-worksheet.md       # Learner-facing passage, 19 questions, answer sheet
├── teacher-answer-key.md      # Correct answers, passage quotes, Chinese explanations
├── student-feedback.md        # Example marking result, evidence and improvement areas
└── student-results.json       # Machine-readable score and per-question results
```

The bundled **original demonstration** contains a four-paragraph passage, 19 IELTS-style reading questions, and sample learner answers. Running the demo gives **14/19 correct (73.7% accuracy)**. This accuracy is specific to this tiny practice set; **it is not an IELTS band score**.

Browse the ready-made examples in [`examples/`](examples/): learner worksheet, teacher key, marking feedback, and a 20-minute reading lesson plan.

### Run checks

```bash
python -m unittest discover -s tests -v
python skills/ielts-reading-tutor/scripts/ielts_tool.py validate --dataset skills/ielts-reading-tutor/assets/sample-exercise.json
```

Tests and the end-to-end demo run automatically on GitHub Actions after pushes and pull requests. GitHub Actions status should be checked on the actual repository page.

## Using the Agent Skill with an AI assistant

Use the folder [`skills/ielts-reading-tutor/`](skills/ielts-reading-tutor/) as the installation/import source in an Agent Skills-compatible product. The exact installation location depends on the product; `SKILL.md` is the entry point.

Sample prompts:

```text
请用雅思阅读老师的方式，给5.5分学生讲解这篇文章。每题标注原文证据，重点讲T/F/NG。
```

```text
请根据我提供的文章生成8道原创雅思阅读判断题。先出学生版，等我提交答案再公布解析。
```

```text
请把这篇文章做成20分钟的雅思阅读试讲，目标学生4.5–6.0分，分别给出学生练习版和教师讲解版。
```

**Supported learning range:** primarily Band 4.5–6.0, with adjustable instruction depth; ability to adapt a lesson does not imply all score bands have been independently evaluated.

## Repository layout

```text
ielts-reading-tutor/
├── README.md
├── demo.py                             # Runs all sample outputs in one command
├── .github/workflows/test.yml          # CI checks
├── examples/                            # Ready-made materials and preview
├── skills/ielts-reading-tutor/
│   ├── SKILL.md                        # Agent instructions
│   ├── agents/openai.yaml              # Optional agent UI metadata
│   ├── assets/                          # Original sample dataset + responses
│   ├── references/                      # Question rules and teaching guidance
│   └── scripts/ielts_tool.py           # validate / render / grade CLI
└── tests/                              # Python tests
```

### Python auto-grading coverage (v1.1)

| Question type | Rule-based validation and grading | Included in demo |
| --- | :---: | :---: |
| True/False/Not Given (`tfng`) | ✅ | ✅ |
| Yes/No/Not Given (`ynng`) | ✅ | — |
| Multiple Choice (`multiple_choice`) | ✅ | ✅ |
| Matching Headings (`matching_headings`) | ✅ | ✅ |
| Matching Information (`matching_information`) | ✅ | ✅ |
| Matching Features (`matching_features`) | ✅ | ✅ |
| Sentence / Summary / Table / Note Completion (`completion`) | ✅ (one answer per numbered blank) | ✅ |
| Short Answer (`short_answer`) | ✅ | ✅ |

The grader uses a **teacher-supplied answer key**, checks answer choices and word limits, then produces per-question evidence and error statistics. Completion tasks are represented as one numbered item per blank. It **does not** autonomously decide whether a novel answer is semantically correct, infer unstated grading keys, or assign an official IELTS band score.

For advanced use, see [dataset format](skills/ielts-reading-tutor/references/dataset-format.md). You can also run `ielts_tool.py` with your own valid JSON questions and answers. The validator checks presence of evidence quotations and basic structure; **logical accuracy and acceptable alternative answers still require teacher review**.

## Quick Start & Verification

1. **Run the demo:** Execute `python demo.py` to generate reproducible worksheets, answer keys, and grading reports without an API key.
2. **Explore the Agent Skill:** Read [`SKILL.md`](skills/ielts-reading-tutor/SKILL.md) for the evidence-first bilingual tutoring workflow.
3. **Review teaching materials:** Browse [`examples/`](examples/) for original reading exercises, answer explanations, and a 20-minute lesson plan.
4. **Run automated tests:** Execute `python -m unittest discover -s tests -v` to verify validation, rendering, and answer-key-based grading.

## Privacy, copyright and license

The sample passage, answer key and student responses are fictional / synthetic. Do not upload identifiable learner records or republish copyrighted exam passages without permission. Code and original demo materials are published under the [MIT License](LICENSE).
