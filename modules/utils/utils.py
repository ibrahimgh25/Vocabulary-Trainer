import warnings, re
import json

import numpy as np

import matplotlib.pyplot as plt

from fuzzywuzzy import fuzz
from collections import Counter

from langdetect import detect
from typing import Union, Iterable, Tuple

def normalize_weights(scores:Iterable[int]) -> np.ndarray:
    """
    Get the weights from a list of scores, this dictates the sampling distribution to
     be used when picking questions
    :param scores: the list of scores (could be positive or negative)
    :returns: a list of weights between 0 and 1
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
    """Randomly selects a key from the list of keys and returns the value of the key and the key itself."""
    keys = [x for x in keys if entry[x] != '']
    key = np.random.choice(keys)
    if len(keys)==1:
        return entry[key], ''
    return entry[key], key

def add_special_chars(answer:str) -> str:
    """Adds special characters to the answer.
    Note: this function is mainly used because I hate typing characters with two dots on top
     and since it's my application I decided to type 'a_' instead of 'ä' and this function
     will replace those instances for me
    """
    special_chars = {'s':'ß', 'a':'ä', 'o':'ö', 'u':'ü', 
                      'A':'Ä', 'O':'Ö', 'U':'Ü', 'S':'ẞ'}
    for char in special_chars.keys():
        # the special char is indicated by the english char proceeded
        # by a '_'
        answer = answer.replace(char + '_', special_chars[char])
    return answer

def delete_list_indecies(list:Iterable, indecies:Iterable[int]) -> Iterable:
    """Deletes a list of indecies from a list.

    :param list: the list to be trimmed
    :param indecies: the list of indices to be removed 

    """
    for index in sorted(indecies, reverse=True):
        del list[index]
    return list

def show_sampling_distribution(low_score=-10, high_score=10, n_samples=10000) -> None:
    """Plots the sampling disctribution given by normalize_weights, just for testing

    :param low_score: the minimum score to show (Default value = -10)
    :param high_score: the maximum score to show (Default value = 10)
    :param n_samples: the number of smaples to take (Default value = 10000)

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

def generate_id(digits:int, existing_ids:Iterable[int]) -> int:
    """
    Generate an id with a fixed number of digits
    :param digits: the number of digits for the id
    :param existing_ids: a list of ids already used
    :returns: a random id not found in the list of existing_ids
    Note: for low 'number of digits to needed ids' ratio should be high for better efficiency
     when generating the ids (so there's a low chance a randomly generated id is found in existing_ids)
    """
    # If not enough ids are available throw and error
    if len(existing_ids) > (10**digits)/2:
        raise Exception('generate_id: the number of ids to be generated can\'t be covered by the specified number of digits')
    # For simpliciy the implementation is faster when the number of available ids is much larger than the number to be assigned
    if len(existing_ids) > (10**digits)/100:
        warnings.warn('generate_id: the number of ids to be generated is close to the number of available ids, for better efficiency increase the number of digits')
    # We have the proper gaurds above to not worry about an open loop
    while(True):
        id = int(10**digits * np.random.rand())
        if id not in existing_ids:
            return id

def matching(answer:str, target:str) -> bool:    
    """
    Sees whether the answer matches the target or not
    :param answer: the answer provided by the user
    :param target: the correct answer
    :returns: True if the answer is matching else False
    """
    correct_answers = re.split(',|;', clean_text(target))
    for value in [get_all_valid_answers(x) for x in correct_answers]:
        correct_answers += value

    answer = clean_text(answer)
    # we'll use the fuzzywuzzy library to have some flexibility, but not too much
    return any([fuzz.ratio(answer, correct_answer.strip()) > 90 for correct_answer in correct_answers])

def get_all_valid_answers(sentences:Union[str, Iterable[str]], choices:Iterable[Tuple[str, Iterable[str]]]=[]):
    """
    Decomposes an answer to all possible implied answers
    :param sentences: a list of valid answers
    :param choices:  the tuple the function got so far, it contains the 
     word and the possible replacementsused by the funtion to guide recursion
    :returns: a list of strings containing the valid answers
    """
    if isinstance(sentences, str):
        sentences = [sentences]
        words_with_slash = re.findall(r'[^ ]+/[^ ]+', sentences[0])    
        choices = [(x, x.split('/')) for x in words_with_slash]
    if len(choices) == 0:
        return sentences
    choice = choices[0]
    choices.remove(choice)
    tmp = sentences
    sentences = []
    for sent in tmp:
        sentences += [sent.replace(choice[0], x, 1) for x in choice[1]]
    return get_all_valid_answers(sentences, choices)

def clean_text(text):
    """  Cleans a string of text for better matching here is a list of what it does:
        - Replace 's and 're with is and are
        - Replace won't, wouldn't and don't... with will not would not and will not...
        - Remove punctiation
        - Remove anything between brackets "()"
        - Change to lower case
        - Remove articles (a, an, and the)
    """
    text = text.lower()
    pairs2replace = {r"\[|\]|\.*|\?||\!":"",
                        '\'re ':' are ',
                        '\'s ':' is ',
                        "won't":"will not",
                        "\'m":" am"
                    }

    for key, replacement in pairs2replace.items():
        text = re.sub(key, replacement, text)
    # Replace all the not abreviations
    regex = re.compile(r"\b[A-Za-z]+n't\b")
    matches = re.findall(regex, text)
    for match in matches:
        replacement = match.replace("n't", " not")
        text = text.replace(match, replacement)
    # Remove everything between paranethesis
    text = re.sub(r"\([a-zA-Z 0-9]*\)", '', text)
    pattern = '|'.join(f'^{x}\s|\s{x}\s' for x in ['a', 'an', 'the'])
    text = re.sub(pattern, ' ', text)
    return text.strip()

def detect_language(text:Union[Iterable, str], lang_mapping_file:str='resources/lang_codes.json'):
    ''' Detects the language of a list of texts or a string of texts'''
    if isinstance(text, Iterable):
        text = ' '.join(text)
    lang_code = detect(text)
    # Try to map the language code to it name, e.g. 'en' -> English
    with open(lang_mapping_file, 'r', encoding='utf-8') as f:
        lang_mapping = json.load(f)
    if lang_code in lang_mapping.keys():
        return lang_mapping[lang_code]
    return 'Target' # If the language code isn't found return a place holder