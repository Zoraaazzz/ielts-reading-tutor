# JSON exercise format

The bundled `assets/sample-exercise.json` is the complete, executable example. Minimal structure:

```json
{
  "meta": {"title": "Original practice title", "level": "5.5", "minutes": 15, "source": "Original fictional educational passage"},
  "paragraphs": [{"label": "A", "text": "..."}],
  "heading_bank": {"i": "A heading", "ii": "Another heading"},
  "questions": [{
    "id": 1,
    "type": "tfng",
    "prompt": "...",
    "answer": "NOT GIVEN",
    "alternatives": [],
    "evidence": {"paragraph": "A", "quote": "exact text from paragraph A"},
    "explanation_zh": "简洁的逻辑说明",
    "skill": "scope"
  }]
}
```

Question types supported by the included CLI: `tfng`, `ynng`, `multiple_choice`, `matching_headings`, `matching_information`, `matching_features`, `completion`, `short_answer`. For multiple choice, add `options` as a map of `A/B/C/D` to option texts and use an option letter as `answer`. For short answers and completions, set integer `word_limit`, and optionally `alternatives` (only for genuinely acceptable equivalent source responses). For headings, use an `answer` key present in `heading_bank`. For `matching_information`, set `answer` to a paragraph label from `paragraphs` (e.g. `"C"`). For `matching_features`, define a `feature_bank` object at dataset level, for example `{"A":"Librarians", "B":"Volunteers", "C":"Survey participants"}`, and use its option label as the answer. For `completion`, create one question per blank, set `word_limit` to an integer, and ensure the answer appears in that question's evidence quote. For sentence, summary, table and note completion, place the surrounding text in `prompt`. Feature/paragraph options may be reused when allowed by the printed instructions. For types not supported in code, the language-model tutor may still explain and draft content directly with evidence, but must not claim the CLI validates those formats.

Sample answer submissions are a JSON object mapping item numbers to strings, for example:

```json
{"1": "TRUE", "2": "FALSE", "3": "NOT GIVEN"}
```

CLI usage (run from the skill directory):

```bash
python scripts/ielts_tool.py validate --dataset assets/sample-exercise.json
python scripts/ielts_tool.py render --dataset assets/sample-exercise.json --mode student --output student.md
python scripts/ielts_tool.py render --dataset assets/sample-exercise.json --mode teacher --output teacher.md
python scripts/ielts_tool.py grade --dataset assets/sample-exercise.json --answers assets/sample-responses.json --format markdown
```

`grade` uses an exact-answer matcher after basic case, whitespace and common TRUE/FALSE/NOT GIVEN alias normalization. It does not infer semantic equivalents, recognize arbitrary paraphrases, or invoke AI. Review unexpected short-answer and completion responses manually; matching requires the supplied answer key and does not prove that a generated item is semantically unambiguous.
