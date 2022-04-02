from typing import Iterable
import numpy as np

def normalize_weights(weights:Iterable) -> np.ndarray:
    """
    Normalizes a list of weights.
    """
    weights = - np.array(weights)
    # Will be changed later to an exponential decay function
    weights = np.where(weights < 0, 0.3 - 1/weights, weights)
    # Emphasis on new words and words that were answered incorrectly
    weights = np.where(weights <= 0, weights + 2, weights)
    return weights / np.sum(weights)

def sample_entry(entry, keys):
    ''' Randomly selects a key from the list of keys and returns the value of the key and the key itself.'''
    keys = [x for x in keys if entry[x] != '']
    key = np.random.choice(keys)
    return entry[key], key

def add_special_chars(answer:str) -> str:
    """
    Adds special characters to the answer.
    """
    special_chars = {'s':'ß', 'a':'ä', 'o':'ö', 'u':'ü', 
                      'A':'Ä', 'O':'Ö', 'U':'Ü', 'S':'ẞ'}
    for char in special_chars.keys():
        # the special char is indicated by the english char proceeded
        # by a '_'
        answer = answer.replace(char + '_', special_chars[char])
    return answer

def delete_list_indecies(list:Iterable, indecies:Iterable[int]) -> Iterable:
    """
    Deletes a list of indecies from a list.
    """
    for index in sorted(indecies, reverse=True):
        del list[index]
    return list



