import unittest

from fuzzywuzzy import fuzz

from modules.answer_evaluators import FuzzyEvaluator


class TestDenseNet(unittest.TestCase):
    def setUp(self):
        self.evaluator = FuzzyEvaluator()


    def test_match_answer(self):
        assert self.evaluator.match_answer("apple", "apple") == True
        assert self.evaluator.match_answer("banana", "apple") == False

    def test_matching(self):
        assert self.evaluator.matching("apple", "apple") == True
        assert self.evaluator.matching("banana", "apple") == False
        assert self.evaluator.matching("apples", "apple") == True
        assert self.evaluator.matching("apple", "apples") == True
        assert self.evaluator.matching("banana", "bananas") == True
        assert self.evaluator.matching("the apple", "apple") == True

        # Test handling of special characters
        assert self.evaluator.matching("Österreich", "Österreich") == True
        assert self.evaluator.matching("Osterreich", "Österreich") == True


    def test_get_all_valid_answers(self):
        assert self.evaluator.get_all_valid_answers("apple") == ["apple"]
        assert self.evaluator.get_all_valid_answers("apple/banana") == ["apple", "banana"]
        assert self.evaluator.get_all_valid_answers("apple/banana/cherry") == ["apple", "banana", "cherry"]

        print(self.evaluator.get_all_valid_answers("apple/banana, cherry/peach"))
        assert self.evaluator.get_all_valid_answers("apple/banana, cherry/peach") == \
               ["apple", "banana", "cherry", "peach"]

        assert self.evaluator.get_all_valid_answers("I love/hate python/php") == \
               ["I love python", "I hate python", "I love php", "I hate php"]