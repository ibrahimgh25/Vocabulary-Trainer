import unittest
import json
import os
from collections import Counter

from modules.support_classes.scores import ScoresHandler

class TestScoresHandler(unittest.TestCase):
    def setUp(self):
        self.scores_file = 'test_scores.json'
        self.scores_dir = "../resources"
        self.loaded_ids = ['1', '2', '3', '4']
        self.scores_handler = ScoresHandler(self.scores_file, self.loaded_ids, self.scores_dir)


    def test_load(self):
        # Test loading scores from file

        self.scores_handler.scores = {'1': 1, '2': 2, '3': 3, '4':0}
        with open(self.scores_handler.scores_path, 'w') as fp:
            json.dump(self.scores_handler.scores, fp)
        scores = self.scores_handler.load(self.loaded_ids)
        self.assertEqual(scores, self.scores_handler.scores)

        # Test loading scores when file does not exist
        os.remove(self.scores_handler.scores_path)
        scores = self.scores_handler.load(self.loaded_ids)
        self.assertEqual(scores, {'1':0, '2':0, '3':0, '4':0})



    def test_save(self):
        self.scores_handler.scores = {'1': 1, '2': 2, '3': 3}
        self.scores_handler.scores_path = f'{self.scores_dir}/testing_output.json'
        self.scores_handler.save()
        with open(self.scores_handler.scores_path, 'r') as fp:
            saved_scores = json.load(fp)
        self.assertEqual(saved_scores, self.scores_handler.scores)



    def test_update(self):
        self.scores_handler.scores = {'1': 1, '2': 2, '3': -4}
        self.scores_handler.update('2', True)
        self.assertEqual(self.scores_handler.scores['2'], 3)
        self.scores_handler.update('2', False)
        self.assertEqual(self.scores_handler.scores['2'], 2)
        self.scores_handler.update('3', True)
        self.assertEqual(self.scores_handler.scores['3'], 0)



    def test_get_weights(self):
        self.scores_handler.scores = {'1': 5, '2': 2, '3': 1, '4':0, '5':-1}
        weights = self.scores_handler.get_weights(['1', '2', '3'])
        # We'll make sure that the element with a lower score gets a higher probability
        self.assertEqual(weights.tolist(), sorted(weights.tolist()))




    def test_remove_id(self):
        self.scores_handler.scores = {'1': 1, '2': 2, '3': 3}
        self.scores_handler.remove_id('2')
        self.assertEqual(self.scores_handler.scores, {'1': 1, '3': 3})


