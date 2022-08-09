''' This package contains util functions to support the language trainer class'''

import re
from fuzzywuzzy import fuzz
from .utils import sample_entry, add_special_chars


def matching(answer, target):    
    correct_answers = re.split(',|;', clean_text(target))
    for value in [get_all_valid_answers(x) for x in correct_answers]:
        correct_answers += value

    answer = re.sub(r'^a\s|^the\s|\sthe\s|\sa\s', '', clean_text(answer), flags=re.IGNORECASE).strip()
    # we'll use the fuzzywuzzy library to have some flexibility, but not too much
    return any([fuzz.ratio(answer, correct_answer.strip()) > 90 for correct_answer in correct_answers])

def get_all_valid_answers(sentences:str, choices=[]):
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
    text = text.lower()
    pairs2replace = {r"\[|\]|\.*|\?||\!":"",
                        '\'re ':' are ',
                        '\'s ':' is ',
                        "won't":"will not"
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
    text = re.sub(r"\(.*\)", '', text)
    pattern = '|'.join(f'^{x}\s|\s{x}\s' for x in ['a', 'an', 'the'])
    text = re.sub(pattern, ' ', text)
    return text.strip()