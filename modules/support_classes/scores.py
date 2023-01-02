import json, os
from typing import Iterable, Union, List
import numpy as np

from collections import Counter
from ..utils import normalize_weights


class ScoresHandler:
    def __init__(self, scores_file, loaded_ids, scores_dir="resources/scores"):
        if not os.path.exists(scores_dir):
            os.mkdir(scores_dir)

        super().__init__()

        self.scores_path = os.path.join(scores_dir, scores_file)
        self.scores = self.load(loaded_ids)

    def load(self, loaded_ids:Iterable[str]) -> dict:
        """Load the scores for a particular task
        :param loaded_ids: the ids loaded from the database, used to drop or add entries to
         the loaded scores
        :returns: a dictionary containing the path to the scores and their values
         e.g. {'path':'path/to/scores', 'scores':{'123432':1, '126432':-3, '123532':2, '123332':5}}
        """
        try:
            scores = json.load(open(self.scores_path, 'r'))
        except FileNotFoundError:
            scores = {}

        # Fill in for the new IDs that still have no entry in the score
        for sample_id in loaded_ids:
            if not str(sample_id) in scores.keys():
                scores[str(sample_id)] = 0
        return scores

    def save(self) -> None:
        """ Saves the updated file back to the file they were loaded from"""
        with open(self.scores_path, 'w') as file_out:
            json.dump(self.scores, file_out)

    def update(self, sample_id:Union[str, int], scored_a_point:bool):
        """ Update the score for a given id based on how the user answered"""
        sample_id = str(sample_id) # Make sure that id is a string
        if scored_a_point:
            self.scores[sample_id] += 1
            # set the row to zero if it's still negative
            self.scores[sample_id] = max(0, self.scores[sample_id])
        else:
            self.scores[sample_id] -= 1

    def get_weights(self, sample_ids:List[Union[int, str]]=None):
        """ Returns a list of weights for given ids
            :param sample_ids: the list of ids included in the sampling process, if empty
             the scores are not filtered
            :returns: a list of numbers between 0 and 1 corresponding to the weights
             of the input ids"""
        if isinstance(sample_ids, list):
            scores = [self.scores[str(x)] for x in sample_ids]
        else:
            scores = self.scores.values()
        return normalize_weights(list(scores))

    def remove_id(self, sample_id:Union[str, int]):
        """ Delete all the scores for a given id"""
        self.scores.pop(str(sample_id))


    def clean_unused_ids(self, used_ids):
        """
        This function is used when you want to remove Ids of entries that are already deleted in the database
        :param used_ids: the ids that are still available in the database
        """
        # Remove scores for words that have been deleted manually by the user
        for sample_id in self.scores.keys():
            if int(sample_id) not in used_ids:
                self.scores.pop(sample_id)


    def summarize(self):
        """ Return a summary to describe certain scores"""
        scores = list(self.scores.values())
        ids = list(self.scores.keys())

        max_idx = scores.index(max(scores))
        min_idx = scores.index(min(scores))

        summary = {
            'average':np.average(scores),
            'min':[ids[min_idx], scores[min_idx]],
            'max':[ids[max_idx], scores[max_idx]],
            'distribution':Counter(scores),
            'entries count':len(scores)
        }
        return summary
