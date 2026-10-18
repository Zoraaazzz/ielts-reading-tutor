# Changelog

## v1.1 — Extended auto-grading coverage

- Added exact-answer validation and grading for matching information, matching features, and one-blank-per-item completion questions.
- Added feature-bank rendering and checks that matching-information keys point to the evidence paragraph.
- Added word-limit enforcement for completion and short-answer submissions.
- Expanded the original, fictional reading demo from 13 to 19 questions, with 14/19 correct sample responses.
- Added 12 more automated tests (24 in total), including missing options, invalid answer keys, word limits, passage evidence, and the Yes/No/Not Given grading path.
- Refreshed student and teacher handouts, demo feedback and README.

### Scope of automated marking

Grading is deterministic and compares submitted answers with a validated, teacher-provided key. It is **not** AI semantic marking and does not predict an official IELTS score. Teachers should review alternative acceptable responses and content quality.
