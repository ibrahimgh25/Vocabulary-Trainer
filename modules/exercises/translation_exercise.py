import re
import numpy as np

from typing import Tuple, Dict, Any

from .exercise import Exercise
from ..answer_evaluators import FuzzyEvaluator
from ..utils.utils import sample_entry

class TranslationExercise(Exercise):
    def __init__(self, scores_path: str, loaded_ids, direction):
        super().__init__(scores_path, loaded_ids)
        assert direction in ['Forward', 'Backward'], 'Direction could only be "Forward" or "Backward"'
        self.direction = direction
        self.evaluator = FuzzyEvaluator()


    def sample_question(self, db_handler) -> dict[str, str]:
        """
        Sample a question for a specific exercise
        :returns: a dictionary with the following form:
         {'question':question_text, 'ID':id, 'target':target}
        """
        # Get the weights to use in the drawing process
        weights = self.scores.get_weights(self.sampled_ids)
        entry = db_handler.sample_random_entry(self.sampled_ids, weights)

        query, target = self.formulate_translation_question(entry)

        if self.direction == 'Forward':
            query = re.sub(r'\([^)]*\)', '', query)
            query = np.random.choice(re.split('[,;]', query)).strip()

        # Save the entry for later reference
        self.question = {'question':query, 'ID':entry['ID'], 'target':target}

        return self.question

    def formulate_translation_question(self, entry:dict)->Tuple[str, str]:
        """
        Formulate the translation question and answer for a database row
        :param entry: dictionary created from the database row
        :returns: a tuple containing the question and the target
        """
        target_keys = ['Translation', 'Translation_f']
        query_keys = ['Word_s', 'Word_p', 'Word_fs', 'Word_fp']
        if self.direction == 'Backward':
            target_keys, query_keys = query_keys, target_keys


        target, target_key = sample_entry(entry, target_keys)
        if '_f' in target_key:
            query_keys = [x for x in query_keys if '_f' in x]
        else:
            query_keys = [x for x in query_keys if not '_f' in x]
        query, query_key = sample_entry(entry, query_keys)
        if self.direction == 'Backward' and target_key != '':
            query = query + ' (' + target_key.split('_')[-1] + ')'

        return query, target

    def evaluate_answer(self, answer: str) -> bool:
        question_id = self.question['ID']
        answered_correctly = self.evaluator.match_answer(answer, self.question['target'])
        self.scores.update(question_id, answered_correctly)
        return answered_correctly
