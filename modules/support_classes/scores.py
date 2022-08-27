import json, os
import numpy as np

from collections import Counter
from ..utils import normalize_weights

class ScoresHandler(dict):
    def __init__(self, sheet_name, loaded_ids):
        if not os.path.exists('resources/scores'):
            os.mkdir('resources/scores')

        super().__init__()
        self['Forward Translate'] = self.load_scores(loaded_ids, 'translate', sheet_name, 'Forward')
        self['Backward Translate'] = self.load_scores(loaded_ids, 'translate', sheet_name, 'Backward')

    def load_scores(self, loaded_ids, *args) -> dict:
        """Load the scores for a particular task

        :param *args: all the arguments should be strings, they're added
         together to create the filename
        :returns: a dictionary containing the path to the score and loaded score
        """
        score_path = 'resources/scores/' + '_'.join([*args]) + '.json'
        try:
            scores = json.load(open(score_path, 'r'))
        except:
            scores = {}
        
        # Fill in for the new IDs that still have no entry in the score
        for id in loaded_ids:
            if not str(id) in scores.keys():
                scores[str(id)] = 0
        # Remove scores for words that have been deleted manually by the user
        for id in list(scores.keys()):
            if int(id) not in loaded_ids:
                scores.pop(id)
        return {'scores':scores, 'path':score_path}
    
    def save_all_scores(self) -> None:
        """ Saves all the scores to their respective files"""
        for score in self.values():
            json.dump(score['scores'], open(score['path'], 'w'))
    
    def update(self, id, exercise, result):
        """"""
        id = str(id) # Make sure that id is a string
        if result:
            self[exercise]['scores'][id] += 1
            # set the row to zero if it's still negative
            self[exercise]['scores'][id] = max(0, self[exercise]['scores'][id])
        elif result == False:
            self[exercise]['scores'][id] -= 1
    
    def get_weights(self, exercise):
        weights = list(self[exercise]['scores'].values())
        return normalize_weights(weights)
    
    def remove_id(self, id):
        for exercise in self.keys():
            self[exercise]['scores'].pop(str(id))
    
    def summarize_scores(self, exercise):
        ''''''
        scores = list(self[exercise]['scores'].values())
        ids = list(self[exercise]['scores'].keys())

        max_idx = scores.index(max(scores))
        min_idx = scores.index(min(scores))

        summary = {
            'average':np.average(scores),
            'min':(ids[min_idx], scores[min_idx]),
            'max':(ids[max_idx], scores[max_idx]),
            'distribution':Counter(scores),
            'entries count':len(scores)
        }
        return summary
