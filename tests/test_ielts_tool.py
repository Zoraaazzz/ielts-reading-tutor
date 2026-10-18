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
        self.assertEqual(result['correct'], 19)
        self.assertEqual(result['accuracy_percent'], 100)

    def test_demo_responses_scored(self):
        result = tool.grade(DATASET, ANSWERS)
        self.assertEqual(result['correct'], 14)
        self.assertEqual(result['total'], 19)
        self.assertEqual(result['attempted'], 19)
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

    def test_new_types_are_in_demo_and_grade_by_type(self):
        result = tool.grade(DATASET, ANSWERS)
        self.assertEqual(result['by_type']['matching_information'], {'correct': 1, 'total': 2})
        self.assertEqual(result['by_type']['matching_features'], {'correct': 1, 'total': 2})
        self.assertEqual(result['by_type']['completion'], {'correct': 2, 'total': 2})
        self.assertEqual(len(result['by_type']), 7)

    def test_matching_information_rejects_unknown_paragraph(self):
        item = copy.deepcopy(DATASET)
        item['questions'][13]['answer'] = 'Z'
        self.assertTrue(any('passage paragraph label' in e for e in tool.validate(item)))

    def test_matching_information_evidence_points_to_answer_paragraph(self):
        item = copy.deepcopy(DATASET)
        item['questions'][13]['answer'] = 'B'
        self.assertTrue(any('matching_information answer does not match evidence paragraph' in e for e in tool.validate(item)))

    def test_matching_features_rejects_missing_option(self):
        item = copy.deepcopy(DATASET)
        item['questions'][15]['answer'] = 'Z'
        self.assertTrue(any('not in feature_bank' in e for e in tool.validate(item)))

    def test_matching_features_requires_feature_bank(self):
        item = copy.deepcopy(DATASET)
        del item['feature_bank']
        self.assertTrue(any('requires a valid feature_bank' in e for e in tool.validate(item)))

    def test_completion_requires_word_limit(self):
        item = copy.deepcopy(DATASET)
        del item['questions'][17]['word_limit']
        self.assertTrue(any('completion requires positive word_limit' in e for e in tool.validate(item)))

    def test_completion_requires_answer_in_evidence(self):
        item = copy.deepcopy(DATASET)
        item['questions'][17]['answer'] = 'nine'
        self.assertTrue(any('completion answer must appear' in e for e in tool.validate(item)))

    def test_completion_rejects_substring_only(self):
        item = copy.deepcopy(DATASET)
        item['questions'][17]['answer'] = 'even'
        self.assertTrue(any('completion answer must appear' in e for e in tool.validate(item)))

    def test_word_limit_applied_to_submissions(self):
        item = copy.deepcopy(DATASET)
        item['questions'][17]['word_limit'] = 1
        result = tool.grade(item, {'18':'seven days'})
        self.assertFalse(result['items'][17]['correct'])
        result = tool.grade(item, {'18':'  SEVEN '})
        self.assertTrue(result['items'][17]['correct'])

    def test_new_question_banks_visible_without_answer_key(self):
        student = tool.render_student(DATASET)
        self.assertIn('Feature bank for matching-features questions', student)
        self.assertIn('**B.** Workshop volunteers', student)
        self.assertIn('**19.** The questionnaire', student)
        self.assertNotIn('### Q16 — B', student)

    def test_ynng_supported_in_cli(self):
        item = copy.deepcopy(DATASET)
        item['questions'][0]['type'] = 'ynng'
        item['questions'][0]['answer'] = 'YES'
        self.assertEqual(tool.validate(item), [])
        graded = tool.grade(item, {'1':'y'})
        self.assertTrue(graded['items'][0]['correct'])

    def test_missing_answer_not_counted_as_attempt(self):
        graded = tool.grade(DATASET, {'17':'', '18':'seven'})
        self.assertEqual(graded['attempted'], 1)
        self.assertEqual(graded['correct'], 1)

    def test_normalization(self):
        self.assertEqual(tool.choice_normalize('  not   given ', 'tfng'), 'NOT GIVEN')
        self.assertEqual(tool.choice_normalize('N.G.', 'tfng'), 'NOT GIVEN')
        self.assertEqual(tool.choice_normalize('Desk   Lamps.', 'short_answer'), 'DESK LAMPS')

if __name__ == '__main__':
    unittest.main()
