"""Run from repo root: python -m unittest discover -s tests -v."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'ielts-reading-tutor'
spec = importlib.util.spec_from_file_location('ielts_tool', SKILL / 'scripts' / 'ielts_tool.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
DATASET = json.loads((SKILL / 'assets' / 'sample-exercise.json').read_text(encoding='utf-8'))
ANSWERS = json.loads((SKILL / 'assets' / 'sample-responses.json').read_text(encoding='utf-8'))

class IELTSReadingToolTests(unittest.TestCase):
    def test_valid_sample(self):
        self.assertEqual(tool.validate(DATASET), [])

    def test_full_key_scores_all(self):
        key = {str(q['id']):q['answer'] for q in DATASET['questions']}
        result = tool.grade(DATASET, key)
        self.assertEqual(result['correct'], 13)
        self.assertEqual(result['accuracy_percent'], 100)

    def test_demo_responses_scored(self):
        result = tool.grade(DATASET, ANSWERS)
        self.assertEqual(result['correct'], 10)
        self.assertEqual(result['total'], 13)
        self.assertEqual(result['attempted'], 13)
        self.assertIn('missing-information', result['error_focus'])

    def test_aliases_and_blank(self):
        result = tool.grade(DATASET, {'1':'t', '2':'f', '4':'ng', '7':'', '8':'b'})
        self.assertEqual(result['correct'], 4)
        self.assertEqual(result['attempted'], 4)

    def test_student_key_not_exposed(self):
        handout = tool.render_student(DATASET)
        self.assertNotIn('Answer key', handout)
        self.assertNotIn('教师版', handout)
        self.assertNotIn('**Q4 — NOT GIVEN**', handout)
        self.assertIn('Answer sheet', handout)
        self.assertIn('Portable projectors', handout) # option labels are fine

    def test_teacher_key_and_evidence(self):
        handout = tool.render_teacher(DATASET)
        self.assertIn('教师版 · Answer key & evidence', handout)
        self.assertIn('**Evidence / 定位：** Paragraph', handout)
        self.assertIn('### Q4 — NOT GIVEN', handout)

    def test_evidence_must_exist(self):
        item = copy.deepcopy(DATASET)
        item['questions'][0]['evidence']['quote'] = 'This sentence never appeared.'
        self.assertTrue(any('quote was not found' in x for x in tool.validate(item)))

    def test_word_limit_validation(self):
        item = copy.deepcopy(DATASET)
        item['questions'][-2]['answer'] = 'some very long answer'
        self.assertTrue(any('exceeds' in x for x in tool.validate(item)))

    def test_duplicate_ids(self):
        item = copy.deepcopy(DATASET)
        item['questions'][1]['id'] = 1
        self.assertTrue(any('unique and sequential' in x for x in tool.validate(item)))

    def test_normalization(self):
        self.assertEqual(tool.choice_normalize('  not   given ', 'tfng'), 'NOT GIVEN')
        self.assertEqual(tool.choice_normalize('N.G.', 'tfng'), 'NOT GIVEN')
        self.assertEqual(tool.choice_normalize('Desk   Lamps.', 'short_answer'), 'DESK LAMPS')

if __name__ == '__main__':
    unittest.main()
