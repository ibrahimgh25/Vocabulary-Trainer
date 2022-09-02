import json, os
from typing import Iterable, Union
import numpy as np

from collections import Counter
from ..utils import normalize_weights

class ScoresHandler(dict):
    def __init__(self, sheet_name:str, loaded_ids:Iterable[int]):
        if not os.path.exists('resources/scores'):
            os.mkdir('resources/scores')

        super().__init__()
        self['Forward Translate'] = self.load(loaded_ids, 'translate', sheet_name, 'Forward')
        self['Backward Translate'] = self.load(loaded_ids, 'translate', sheet_name, 'Backward')

    def load(self, loaded_ids:Iterable[str], *args) -> dict:
        """Load the scores for a particular task
        :param loaded_ids: the ids loaded from the database, used to drop or add entries to
         the loaded scores
        :param *args: all the arguments should be strings, they're added
         together to create the filename
        :returns: a dictionary containing the path to the scores and their values
         e.g. {'path':'path/to/scores', 'scores':{'123432':1, '126432':-3, '123532':2, '123332':5}}
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
    
    def update(self, id:Union[str, int], exercise:str, result:bool):
        """ Update the score for a given id based on how the user answered"""
        id = str(id) # Make sure that id is a string
        if result:
            self[exercise]['scores'][id] += 1
            # set the row to zero if it's still negative
            self[exercise]['scores'][id] = max(0, self[exercise]['scores'][id])
        elif result == False:
            self[exercise]['scores'][id] -= 1
    
    def get_weights(self, exercise:str, ids:Iterable[Union[int, str]]=[]):
        ''' Returns a list of weights for given ids
            :param exercise: the name of the exercise used for the scores
            :param ids: the list of ids included in the sampling process, if empty
             the scores are not filtered
            :returns: a list of numbers between 0 and 1 corresponding to the weights
             of the input ids'''
        if len(ids) > 0:
            scores = [self[exercise]['scores'][str(x)] for x in ids]
        else:
            scores = self[exercise]['scores'].values()
        return normalize_weights(list(scores))
    
    def remove_id(self, id:Union[str, int]):
        ''' Delete all the scores for a given id'''
        for exercise in self.keys():
            self[exercise]['scores'].pop(str(id))
    
    def summarize(self, exercise:str):
        ''' Return a summary to describe certain scores'''
        scores = list(self[exercise]['scores'].values())
        ids = list(self[exercise]['scores'].keys())

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
