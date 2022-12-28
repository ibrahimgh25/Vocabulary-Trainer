import unittest

from modules.exercises import TranslationExercise
from modules.answer_evaluators import FuzzyEvaluator


class TestTranslationExercise(unittest.TestCase):
    def test_init(self):
        exercise = TranslationExercise(scores_path='scores.json', loaded_ids=[1, 2, 3], direction='Forward')
        self.assertEqual(exercise.direction, 'Forward')
        self.assertIsInstance(exercise.evaluator, FuzzyEvaluator)

        exercise = TranslationExercise(scores_path='scores.json', loaded_ids=[1, 2, 3], direction='Backward')
        self.assertEqual(exercise.direction, 'Backward')
        self.assertIsInstance(exercise.evaluator, FuzzyEvaluator)

        with self.assertRaises(AssertionError):
            exercise = TranslationExercise(scores_path='scores.json', loaded_ids=[1, 2, 3], direction='Incorrect')

    def test_sample_question(self):
        # Set up mock db_handler
        class DummyDBHandler:
            def sample_random_entry(self, ids, weights):
                return {'ID': 1, 'Word_s': 'apple', 'Word_p': 'apples', 'Word_fs': '', 'Word_fp': '',
                        'Translation': 'manzana', 'Translation_f': ''}

        exercise = TranslationExercise(scores_path='scores.json', loaded_ids=[1, 2, 3], direction='Forward')
        question = exercise.sample_question(DummyDBHandler())
        self.assertEqual(question, {'question': 'apple', 'ID': 1, 'target': 'manzana'})
        self.assertEqual(exercise.question, {'question': 'apple', 'ID': 1, 'target': 'manzana'})

        exercise = TranslationExercise(scores_path='scores.json', loaded_ids=[1, 2, 3], direction='Backward')
        question = exercise.sample_question(DummyDBHandler())
        self.assertEqual(question, {'question': 'manzana', 'ID': 1, 'target': 'apple'})
        self.assertEqual(exercise.question, {'question': 'manzana', 'ID': 1, 'target': 'apple'})

    def test_formulate_translation_question(self):
        exercise = TranslationExercise(scores_path='scores.json', loaded_ids=[1, 2, 3], direction='Forward')
        entry = {'ID': 1, 'Word_s': 'apple', 'Word_p': 'apples', 'Word_fs': '', 'Word_fp': '',
                 'Translation': 'manzana', 'Translation_f': ''}
        question, target = exercise.formulate_translation_question(entry)
        self.assertEqual(question, 'apple')
        self.assertEqual(target, 'manzana')

        entry = {'ID': 1, 'Word_s': 'apple', 'Word_p': 'apples', 'Word_fs': 'apples (f)', 'Word_fp': 'apples (p)', 'Translation': 'manzana', 'Translation_f': 'manzanas (f)'}
        question, target = exercise.formulate_translation_question(entry)
        self.assertIn(question, ['apple', 'apples (f)', 'apples (p)'])
        self.assertEqual(target, 'manzana')

        exercise = TranslationExercise(scores_path='scores.json', loaded_ids=[1, 2, 3], direction='Backward')
        entry = {'ID': 1, 'Word_s': 'apple', 'Word_p': 'apples', 'Word_fs': '', 'Word_fp': '',
                 'Translation': 'manzana', 'Translation_f': ''}
        question, target = exercise.formulate_translation_question(entry)
        self.assertEqual(question, 'manzana')
        self.assertEqual(target, 'apple')

        entry = {'ID': 1, 'Word_s': 'apple', 'Word_p': 'apples', 'Word_fs': 'apples (f)', 'Word_fp': 'apples (p)',
                 'Translation': 'manzana', 'Translation_f': 'manzanas (f)'}
        question, target = exercise.formulate_translation_question(entry)
        self.assertEqual(question, 'manzana (s)')
        self.assertIn(target, ['apple', 'apples (f)', 'apples (p)'])

    def test_evaluate_answer(self):
        # Set up mock evaluator
        class DummyEvaluator:
            def match_answer(self, answer, target):
                return answer == target

        exercise = TranslationExercise(scores_path='scores.json', loaded_ids=[1, 2, 3], direction='Forward')
        exercise.question = {'question': 'apple', 'ID': 1, 'target': 'manzana'}
        exercise.evaluator = DummyEvaluator()

        self.assertTrue(exercise.evaluate_answer('manzana'))
        self.assertFalse(exercise.evaluate_answer('banana'))