from abc import abstractmethod

import numpy as np

from ..support_classes.scores import ScoresHandler

class Exercise:
    def __init__(self, scores_path, loaded_ids):
        self.scores = ScoresHandler(scores_path, loaded_ids)

        self.sampled_ids = loaded_ids

        self.question = None

    @abstractmethod
    def sample_question(self, db_handler) -> dict[str, str]:
        """
        Sample a question for a specific exercise
        :returns: a dictionary with the following form:
         {'question':question_text, 'ID':id, 'target':target}
        """
        pass

    @abstractmethod
    def evaluate_answer(self, answer:str) -> bool:
        pass

    def set_sampled_ids(self, loaded_ids, redraw:int=-1):
        if redraw > 0:
            weights = self.scores.get_weights()
            self.sampled_ids = np.random.choice(loaded_ids, p=weights, replace=False, size=redraw)
        else:
            self.sampled_ids = loaded_ids


    def save_scores(self):
        self.scores.save()