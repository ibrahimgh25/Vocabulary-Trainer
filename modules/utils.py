
import numpy as np
import matplotlib.pyplot as plt

from collections import Counter
from typing import Iterable
def normalize_weights(scores:Iterable) -> np.ndarray:
    """
    Return a list of weights based on scores of the answers.
    """
    weights = np.array(scores)
    # Assign weights for the words that were answered incorrectly or not seen yet.
    # The weights are proportional to the number of times the word was answered incorrectly.
    weights = np.where(weights <= 0, weights - 3, weights)
    # Assign weights for the words that were answered correctly before.
    # The weights are inversely proportional to the number of times the word was answered correctly
    weights = np.where(weights > 0, -2/weights, weights)
    # Assign only small chance for the words that were answered correctly more than 10 times.
    weights = np.where(weights > -2/10, -0.01, weights)
    return weights / np.sum(weights)

def sample_entry(entry, keys):
    ''' Randomly selects a key from the list of keys and returns the value of the key and the key itself.'''
    keys = [x for x in keys if entry[x] != '']
    key = np.random.choice(keys)
    if len(keys)==1:
        return entry[key], ''
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

def show_sampling_distribution(low_score=-10, high_score=10, n_samples=10000) -> None:
    """
    Plots the sampling disctribution given by normalize_weights.
    """
    # Make sure that low_score is smaller than high_score
    if low_score > high_score:
        low_score, high_score = high_score, low_score
    
    scores = np.arange(int(low_score), int(high_score), 1)
    weights = normalize_weights(scores)
    draws = np.random.choice(scores, size=n_samples, p=weights)
    # Count how many times each score was picked
    counts = Counter(draws)
    
    counts = [(x, y) for x, y in counts.items()]
    counts.sort(key=lambda x: x[0])
    # Plot the distribution
    plt.plot(range(len(counts)), [x[1] for x in counts])
    plt.show()